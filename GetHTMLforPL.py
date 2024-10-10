from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time

# Set the path to your WebDriver (Chrome in this example)
webdriver_path = r'chromedriver-win64\chromedriver.exe'

# Create a Service object for ChromeDriver
service = Service(webdriver_path)

# Initialize the WebDriver (Chrome)
driver = webdriver.Chrome(service=service)

# Open the SteamDB URL
url = 'https://steamdb.info/tag/1003823/'
driver.get(url)

# Optional: Wait for the page to load fully
time.sleep(5)  # Adjust this time as necessary

# Locate the dropdown element using XPath
dropdown = driver.find_element(By.XPATH, '//*[@id="dt-length-0"]')

# Create a Select object to interact with the dropdown
select = Select(dropdown)

# Select the option with the value "-1" (All (slow))
select.select_by_value('-1')
print("Option to show all game selected")

# Wait for the page to reload with all the data (adjust time if necessary)
print('Waiting for the page to load all games')
time.sleep(10)

# Get the page source (HTML)
html_content = driver.page_source

# Save the HTML content to a file
with open(r'HTML\PL.html', 'w', encoding='utf-8') as file:
    file.write(html_content)

print("HTML page saved successfully.")

# Close the browser
driver.quit()
