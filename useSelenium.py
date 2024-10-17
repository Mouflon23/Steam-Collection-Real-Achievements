from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def create_webdriver():
    
    webdriver_path = r'chromedriver-win64\chromedriver.exe'

    # Setup WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run headless browser if you don't need GUI
    # Set the path to your WebDriver (Chrome in this example)
    # Suppress logs by redirecting them to NUL (Windows equivalent of /dev/null)
    service = Service(webdriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    #driver = webdriver.Chrome(service=service)

    return driver
