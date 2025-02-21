import os
import requests
import base64
import time
from datetime import datetime
from urllib.parse import urlparse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, StaleElementReferenceException
from requests.exceptions import RequestException
from config.config import Config

class LinkChecker:
    # Updated special domains with validation rules
    SPECIAL_DOMAINS = {
        'twitter.com': {'method': 'GET', 'valid_codes': [200, 400, 401, 403]},
        'x.com': {'method': 'GET', 'valid_codes': [200, 400, 401, 403]},
        'facebook.com': {'method': 'GET', 'valid_codes': [200, 400, 401, 403]},
        'instagram.com': {'method': 'GET', 'valid_codes': [200, 400, 401, 403]},
        'linkedin.com': {'method': 'GET', 'valid_codes': [200, 400, 401, 403]},
        'tiktok.com': {'method': 'GET', 'valid_codes': [200, 400, 401, 403]},
        'youtube.com': {'method': 'GET', 'valid_codes': [200, 400, 401, 403]},
        'pinterest.com': {'method': 'GET', 'valid_codes': [200, 400, 401, 403]}
    }

    def __init__(self, driver):
        self.driver = driver
        self.broken_links = []
        self.passed_links = []
        os.makedirs(Config.REPORTS_DIR, exist_ok=True)
        self.report_template = self._load_template()
        self.total_links = 0
        self.current_link = 0
        self.session = self._create_session()

    def _create_session(self):
        """Create a session with custom headers."""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        return session

    def _load_template(self):
        template_path = os.path.join(os.path.dirname(__file__), 'report_template.html')
        with open(template_path, 'r') as f:
            return f.read()

    def wait_for_page_load(self, timeout=10):
        """Wait for the page to be fully loaded."""
        try:
            # Wait for document.readyState to be complete
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            
            # Wait for jQuery if it exists
            jquery_ready = """
                return typeof jQuery === 'undefined' || jQuery.active === 0
            """
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script(jquery_ready)
            )
            
            # Additional wait for any animation to complete
            time.sleep(1)
            return True
        except TimeoutException:
            return False

    def get_all_links(self):
        """Enhanced link gathering with better error handling."""
        links = []
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "a"))
                )
                
                elements = self.driver.find_elements(By.TAG_NAME, "a")
                
                for element in elements:
                    try:
                        href = element.get_attribute('href')
                        text = element.text or element.get_attribute('title') or element.get_attribute('aria-label') or '[No text]'
                        
                        if href and not href.startswith('javascript:') and not href.startswith('#'):
                            links.append({
                                'url': href,
                                'text': text
                            })
                    except StaleElementReferenceException:
                        continue
                    except Exception as e:
                        print(f"\nError processing link: {str(e)}")
                        continue
                        
                break  # Success, exit retry loop
                
            except TimeoutException:
                if attempt == max_retries - 1:
                    print("\nFailed to load page after multiple attempts")
                time.sleep(2)  # Wait before retry
                
        return links

    def check_link(self, url, max_retries=2):
        """Enhanced link checking with retries and better validation."""
        if not url or url.startswith('javascript:') or url.startswith('#'):
            return True

        domain = urlparse(url).netloc
        special_domain = next((d for d in self.SPECIAL_DOMAINS if d in domain), None)
        method = self.SPECIAL_DOMAINS[special_domain]['method'] if special_domain else 'HEAD'
        valid_codes = self.SPECIAL_DOMAINS[special_domain]['valid_codes'] if special_domain else [200]

        for attempt in range(max_retries):
            try:
                if method == 'HEAD':
                    response = self.session.head(url, allow_redirects=True, timeout=Config.TIMEOUT)
                    if response.status_code == 405:  # Method not allowed
                        response = self.session.get(url, timeout=Config.TIMEOUT)
                else:
                    response = self.session.get(url, timeout=Config.TIMEOUT)

                is_success = response.status_code in valid_codes
                
                if not is_success:
                    print(f"\nWarning: {url} returned status code {response.status_code}")
                    if attempt < max_retries - 1:
                        time.sleep(1)  # Wait before retry
                        continue
                
                return is_success
                
            except RequestException as e:
                print(f"\nError checking {url}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(1)  # Wait before retry
                    continue
                return False

    def verify_page_content(self):
        """Verify if the page has actual content."""
        try:
            # Check if body has content
            body = self.driver.find_element(By.TAG_NAME, "body")
            if not body.text.strip():
                return False

            # Check if page has basic elements
            main_content = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'content') or contains(@class, 'main')]")
            if not main_content:
                return False

            return True
        except Exception:
            return False

    def capture_screenshot(self, url):
        current_url = self.driver.current_url
        try:
            self.driver.get(url)
            
            # Wait for page load and verify content
            if not self.wait_for_page_load():
                print(f"\nWarning: Page load timeout for {url}")
            
            if not self.verify_page_content():
                print(f"\nWarning: Possible empty or invalid content at {url}")
            
            # Take screenshot after ensuring page is ready
            screenshot = self.driver.get_screenshot_as_base64()
            return f"data:image/png;base64,{screenshot}"
        except WebDriverException as e:
            print(f"\nError capturing screenshot for {url}: {str(e)}")
            return ""
        finally:
            # Return to the original page
            self.driver.get(current_url)
            self.wait_for_page_load()

    def generate_report(self):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        report_path = os.path.join(Config.REPORTS_DIR, report_filename)
        
        # Generate broken links HTML
        link_results = ""
        for link in self.broken_links:
            link_results += f"""
                <div class="link-card">
                    <h3>Broken Link Found</h3>
                    <p><strong>URL:</strong> <span class="error">{link['url']}</span></p>
                    <p><strong>Link Text:</strong> {link['text']}</p>
                    <h4>Screenshot:</h4>
                    <img src="{link['screenshot']}" class="screenshot" alt="Error Screenshot">
                </div>
            """

        # Generate passed links HTML with screenshots
        passed_results = "<ul>"
        for link in self.passed_links:
            passed_results += f"""
                <li class="link-card">
                    <p><strong>URL:</strong> <a href="{link['url']}" target="_blank" class="success">{link['url']}</a></p>
                    <p><strong>Link Text:</strong> {link['text']}</p>
                    <h4>Screenshot:</h4>
                    <img src="{link['screenshot']}" class="screenshot" alt="Success Screenshot">
                </li>
            """
        passed_results += "</ul>"

        # Auto-open broken links section if there are any
        broken_open = "open" if self.broken_links else ""

        report_content = self.report_template.format(
            timestamp=timestamp,
            base_url=Config.BASE_URL,
            total_links=self.total_links,
            total_passed=len(self.passed_links),
            total_broken=len(self.broken_links),
            link_results=link_results,
            passed_results=passed_results,
            broken_open=broken_open
        )

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return report_path

    def check_all_links(self):
        self.driver.get(Config.BASE_URL)
        links = self.get_all_links()
        self.total_links = len(links)
        
        for idx, link in enumerate(links):
            self.current_link = idx + 1
            percentage = (self.current_link / self.total_links) * 100
            print(f"\rProgress: {percentage:.1f}% ({self.current_link}/{self.total_links})", end="")
            
            # Check if link is broken
            is_working = self.check_link(link['url'])
            
            # Capture screenshot by visiting the URL
            screenshot = self.capture_screenshot(link['url'])
            
            if not is_working:
                self.broken_links.append({
                    'url': link['url'],
                    'text': link['text'],
                    'screenshot': screenshot
                })
            else:
                self.passed_links.append({
                    'url': link['url'],
                    'text': link['text'],
                    'screenshot': screenshot
                })
            
            # Return to homepage
            self.driver.get(Config.BASE_URL)
            self.wait_for_page_load()
        
        print("\nLink checking completed!")
        return self.broken_links
