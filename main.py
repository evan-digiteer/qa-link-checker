import webbrowser
import os
from utils.webdriver import setup_driver
from utils.link_checker import LinkChecker
from config.config import Config

def main():
    driver = setup_driver()
    try:
        print(f"Starting link check for: {Config.BASE_URL}")
        checker = LinkChecker(driver)
        broken_links = checker.check_all_links()
        
        print("\n" + "="*50)
        if broken_links:
            print(f"\nFound {len(broken_links)} broken links:")
            for link in broken_links:
                print(f"\nURL: {link['url']}")
                print(f"Text: {link['text']}")
            
            report_path = checker.generate_report()
            print(f"\nDetailed report generated: {report_path}")
            webbrowser.open(f"file://{os.path.abspath(report_path)}")
        else:
            print("\nNo broken links found! ✓")
            
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
