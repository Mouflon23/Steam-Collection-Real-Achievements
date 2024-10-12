from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
import json
from bs4 import BeautifulSoup

def extract_links_to_json(input_html, output_json):
    # Load the HTML file
    with open(input_html, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse the HTML
    soup = BeautifulSoup(html_content, 'lxml')

    # Find all <a> tags with the specified class and target
    links = soup.find_all('a', class_='b', target='_blank')

    # Extract the text content into a list
    extracted_texts = [link.text for link in links]

    # Save the extracted text content to a JSON file
    with open(output_json, 'w', encoding='utf-8') as json_file:
        json.dump(extracted_texts, json_file, ensure_ascii=False, indent=4)

    print(f"Extracted text content has been saved to {output_json}.")

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
print("Wait for the page to load...")

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

print("HTML page saved successfully for Profil Limited.")

# Close the browser
driver.quit()

print("Go to your browser.")
print()
print("Use this adress => https://steamdb.info/sales/?category=777&min_discount=0&min_rating=0&min_reviews=0")
print()
print("Find the '*** entries per page' and use the option 'All(slow)'.")
print("Ctrl+S and save html file in folder HTML with name 'SIL.html'.")

# waiting to get to next step
input("Press Enter when previous task is done...")

# Process PL.html
extract_links_to_json(r'HTML\PL.html', r'JSON\PL.json')

# Process SIL.html
extract_links_to_json(r'HTML\SIL.html', r'JSON\SIL.json')
