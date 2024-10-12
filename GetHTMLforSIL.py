from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import time

# Set the path to your WebDriver (Chrome in this example)
webdriver_path = r'chromedriver-win64\chromedriver.exe'

# Set the path to the Chrome extension (.crx file)
extension_path = r'SteamDB - Chrome Web Store 4.7.0.0.crx'

# Create a ChromeOptions object
chrome_options = Options()

# Add the extension to ChromeOptions
chrome_options.add_extension(extension_path)

# Create a Service object for ChromeDriver
service = Service(webdriver_path)

# Initialize the WebDriver (Chrome) with the options
driver = webdriver.Chrome(service=service, options=chrome_options)

# Open the SteamDB URL
url = 'https://steamdb.info/sales/?min_reviews=0&min_rating=0&min_discount=0&displayOnly=OwnedGames&category=777'
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

# # Wait for the page to reload with all the data (adjust time if necessary)
# print('Waiting for the page to load all games')
# time.sleep(10)

# # Get the page source (HTML)
# html_content = driver.page_source

# # Save the HTML content to a file
# with open(r'HTML\SIL.html', 'w', encoding='utf-8') as file:
#     file.write(html_content)

# print("HTML page saved successfully.")

# # Close the browser
# driver.quit()
