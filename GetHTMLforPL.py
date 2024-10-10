from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import os

# Set the path to your WebDriver (Chrome in this example)
webdriver_path = r'C:\Users\super\Documents\Dev\Steam-Collection-Games-Success\chromedriver-win64\chromedriver.exe'  # Update with your actual path

# Create a Service object for ChromeDriver
service = Service(webdriver_path)

# Initialize the WebDriver (Chrome)
driver = webdriver.Chrome(service=service)

# Open the SteamDB URL
url = 'https://steamdb.info/tag/1003823/'
driver.get(url)

# Optional: Wait for the page to load fully
time.sleep(5)  # Adjust this time as necessary

# Get the page source (HTML)
html_content = driver.page_source

# Ensure the directory exists
os.makedirs(r'Steam-Collection-Games-Success\HTML', exist_ok=True)

# Save the HTML content to a file
with open(r'Steam-Collection-Games-Success\HTML\PL.html', 'w', encoding='utf-8') as file:
    file.write(html_content)

print("HTML page saved successfully.")

# Close the browser
driver.quit()
