from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Setup WebDriver
chrome_options = Options()
#chrome_options.add_argument("--headless")  # Run headless browser if you don't need GUI
# Set the path to your WebDriver (Chrome in this example)
webdriver_path = r'chromedriver-win64\chromedriver.exe'
service = Service(webdriver_path)
#driver = webdriver.Chrome(service=service, options=chrome_options)
driver = webdriver.Chrome(service=service)

# Open the Steam app page
app_id = '2905170'  # Replace with the actual app id
url = f'https://store.steampowered.com/app/{app_id}'
driver.get(url)

# Find the element by XPath
element_xpath = '//*[@id="category_block"]/div[1]'
element = driver.find_element(By.XPATH, element_xpath)

# Get the text or other attributes
text = element.text  # This gets the visible text from the element
print("Extracted Information: ", text)

# Check if neither of the phrases are in the text
if not ("Steam essaye d'en apprendre plus sur ce jeu" in text or "Fonctionnalités de profil limitées" in text):
    # Do something if the phrases are NOT present
    print("Neither phrase found!")
else:
    # Do something if one of the phrases IS present
    print("One of the phrases found.")

# Close the browser
driver.quit()