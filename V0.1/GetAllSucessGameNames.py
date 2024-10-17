import pyautogui
import pytesseract
import json
import cv2
import numpy as np
import time
import os
import pyperclip
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Setup WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run headless browser if you don't need GUI
# Set the path to your WebDriver (Chrome in this example)
webdriver_path = r'chromedriver-win64\chromedriver.exe'
service = Service(webdriver_path)


def get_item_position(item):
    # Get the current mouse position
    print(f"Move the mouse to {item}...")
    input("Press Enter when task is done...")
    x, y = pyautogui.position()

    # Assign the position to a variable in the desired format
    value = (x, y)
    return value

def is_text_visible(region=None):
    # Take a screenshot
    screenshot = pyautogui.screenshot(region=region)
    # Save the screenshot as a .png file
    # screenshot.save(f"screenshot_.png")
    
    # Convert the screenshot to a numpy array and to grayscale
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Use pytesseract to extract text
    extracted_text = pytesseract.image_to_string(gray_img)

    # Check if any of the target variations are in the extracted text
    return any(target_text.lower() in extracted_text for target_text in target_texts)

def get_game_name(game_id):
    # Construct the URL using the provided game ID
    url = f"https://store.steampowered.com/api/appdetails?appids={game_id}"
    
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        
        # Navigate through the JSON to get the game name
        if str(game_id) in data and data[str(game_id)]['success']:
            game_name = data[str(game_id)]['data']['name']
            return game_name
        else:
            return f"Game ID {game_id} not found or not available."
    else:
        return f"Failed to retrieve data. Status code: {response.status_code}"

# Define the region for checking "SUCCES" (x, y, width, height)
check_region = (1580, 530, 315, 430)  # Define the region for checking "SUCCES"

# Define the variations of "SUCCES" to check
target_texts = ["SUCCES", "succés", "succes"]

print()

print("Click a game on your game library...")
store_page = get_item_position('store page')
pyautogui.click(store_page)
game_url = get_item_position('game url')
go_back = get_item_position('go back')
pyautogui.click(go_back)
print("Scroll to the last game in your library.")
print("Click on it in your game library...")
input("Press Enter when previous task is done...")
# Click store page
pyautogui.click(store_page)
time.sleep(1)
# Click game_page
pyautogui.click(game_url)
game_page = pyperclip.paste()
# Click back to Library
time.sleep(1)
pyautogui.click(go_back)
# Extract the game name
game_id = game_page.split('/')[-3].replace('_', ' ')  # Get appID
last_game_name = get_game_name(game_id)
print(f'Last game : {last_game_name}')
print("Go to the top of your games library")
input("Press Enter when previous task is done...")

# Pause for a moment to set up your screen
print("Click on top of games library...")
time.sleep(5)

# Initialize the list for games with achievements
games_with_achievements = []
game_name_a = None

j = 1
while(True):
    print(f'Game n°{j}')
    if is_text_visible(region=check_region):
        print("Success Detected!")
        
        # Click store page
        pyautogui.click(store_page)
        time.sleep(1)
        # Click game_page
        pyautogui.click(game_url)
        game_page = pyperclip.paste()
        # Click back to Library
        time.sleep(1)
        pyautogui.click(go_back)
        pyautogui.press('tab')
        # Extract the game name
        game_id = game_page.split('/')[-3].replace('_', ' ')  # Get appID

        driver = webdriver.Chrome(service=service, options=chrome_options)
        #driver = webdriver.Chrome(service=service)
        # Verification PL SIL in steam
        url = f'https://store.steampowered.com/app/{game_id}'
        driver.get(url)
        # Find the element by XPath
        element_xpath = '//*[@id="category_block"]/div[1]'
        element = driver.find_element(By.XPATH, element_xpath)
        # Get the text or other attributes
        text = element.text  # This gets the visible text from the element
        # Check if neither of the phrases are in the text
        # Close the browser after retrieving and processing everything
        driver.quit()
        game_name_a = get_game_name(game_id)
        print(f"Game {j}: {game_name_a}")

        if not ("Steam essaye d'en apprendre plus sur ce jeu" in text or "Fonctionnalités de profil limitées" in text):
            
            # Add the game name to the list
            games_with_achievements.append(game_name_a)
            print(f"Game {j} added to Achievement.json")

            # Save the games with achievements to a JSON file immediately
            output_file = r'JSON\Achievement.json'
            if os.path.exists(output_file):
                # Load the existing data if the file already exists
                with open(output_file, 'r', encoding='utf-8') as file:
                    data = json.load(file)
            else:
                data = []

            # Append new games to the existing data
            data.append(game_name_a)

            # Write the updated data back to the JSON file
            with open(output_file, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

            print("Achievement.json updated with the new game.")
        else:
            print("Game with PL or SIL. Not saved.")

    # Check for exit conditions
    # NOT WORKING IF GAME DO NOT HAVE SUCCESS, NEED TO FIND SOLUTIONS
    if last_game_name == game_name_a:
        break
    # Press the Down Arrow key to scroll down
    pyautogui.press('down')
    j += 1
    print()
    print(f"> NEXT GAME.")
    time.sleep(3)

print("All Games with Achievements have been added to Achievement.json")