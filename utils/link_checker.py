import os
import requests
import base64
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from config.config import Config

class LinkChecker:
    def __init__(self, driver):
        self.driver = driver
        self.broken_links = []
        self.passed_links = []
        os.makedirs(Config.REPORTS_DIR, exist_ok=True)
        self.report_template = self._load_template()
        self.total_links = 0
        self.current_link = 0

    def _load_template(self):
        template_path = os.path.join(os.path.dirname(__file__), 'report_template.html')
        with open(template_path, 'r') as f:
            return f.read()

    def get_all_links(self):
        """Get all links and their details before processing."""
        links = []
        elements = self.driver.find_elements(By.TAG_NAME, "a")
        
        for element in elements:
            try:
                href = element.get_attribute('href')
                text = element.text
                if href and not href.startswith('javascript:') and not href.startswith('#'):
                    links.append({
                        'url': href,
                        'text': text
                    })
            except:
                continue
        
        return links

    def check_link(self, link):
        try:
            href = link.get_attribute('href')
            if not href or href.startswith('javascript:') or href.startswith('#'):
                return True

            response = requests.head(href, allow_redirects=True, timeout=Config.TIMEOUT)
            return response.status_code < 400
        except:
            return False

    def capture_screenshot(self, url):
        current_url = self.driver.current_url
        try:
            self.driver.get(url)
            screenshot = self.driver.get_screenshot_as_base64()
            return f"data:image/png;base64,{screenshot}"
        except WebDriverException as e:
            print(f"\nError capturing screenshot for {url}: {str(e)}")
            return ""
        finally:
            # Return to the original page
            self.driver.get(current_url)

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
            
            # Check if link is broken using requests
            try:
                response = requests.head(link['url'], allow_redirects=True, timeout=Config.TIMEOUT)
                is_working = response.status_code < 400
            except:
                is_working = False
            
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
        
        print("\nLink checking completed!")
        return self.broken_links
