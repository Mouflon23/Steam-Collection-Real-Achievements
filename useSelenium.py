from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def create_webdriver():
    # Setup WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run headless browser if you don't need GUI
    # Use ChromeDriverManager to automatically manage the ChromeDriver version
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    return driver