from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-webrtc')
    chrome_options.add_argument('--disable-features=WebRTC')
    chrome_options.add_argument('--disable-features=WebRTCStunProbing')
    
    driver = webdriver.Chrome(
        options=chrome_options
    )
    return driver
