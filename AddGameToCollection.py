import cv2
import numpy as np
import pyautogui
import json
import pytesseract
import requests
import pyperclip
import time
from useSelenium import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def read_json(file_path):

    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

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

def get_game_url(store_page, game_url, go_back):
    have_page = False
    # Click store page
    pyautogui.click(store_page)
    
    while True:
        time.sleep(2)
        # Click game_page
        pyautogui.click(game_url)
        game_page = pyperclip.paste()
        # Check if the game_page contains 'https://store.steampowered.com/?snr='
        if 'https://store.steampowered.com/?snr=' not in game_page:
            if game_page != "https://store.steampowered.com/":
                have_page = True
                # Click back to Library
                time.sleep(1)
                pyautogui.click(go_back)
                pyautogui.press('tab')
                # Extract the game name
                game_id = game_page.split('/')[-3].replace('_', ' ')  # Get appID
                game_name = get_game_name(game_id)
                break
            else:
                game_id = None
                game_name = None
                pyautogui.click(go_back)
                pyautogui.press('tab')
                print("Game page does not exist!")
                break

    return game_id, game_name, have_page


    
def setup_library(last_game_name):
    
    print(f'Last game : {last_game_name}')
    print("Go to the top of your games library")
    input("Press Enter when previous task is done...")
    print("Click the first game in 3 seconds")
    print()
    time.sleep(3)

    return last_game_name

def check_success(target_texts, region=None):

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

def add_game_to_collection():

    game_settings = (1789, 431)
    add_to = (1705, 497)
    collection_success = (1448, 699)

    # add game to collection
    pyautogui.click(game_settings)
    time.sleep(1)
    pyautogui.click(add_to)
    time.sleep(1)
    pyautogui.click(collection_success)
    time.sleep(1)
    pyautogui.click(game_settings)
    print("Game added to collection")

def compare_game_with_json(game_name):

    is_find = False
    # Read the JSON files with UTF-8 encoding and BOM handling
    pl = read_json(r'JSON\PL.json')
    sil = read_json(r'JSON\SIL.json')
    if game_name in pl or game_name in sil:
        is_find = True

    return is_find

from selenium.webdriver.common.by import By

def check_steam_page(game_id, current_game, error_list):
    driver = create_webdriver()
    url = f'https://store.steampowered.com/app/{game_id}'
    driver.get(url)

    try:
        # Locate the element by class name using By.CLASS_NAME
        category_block = driver.find_element(By.CLASS_NAME, "game_area_features_list_ctn")
        
        info_game = category_block.text  # Extract the text from the first div
    except Exception as e:
        info_game = "Error"
        game_error = current_game
        error_list.append(game_error)
        # Step 5: Save the filtered achievements to AchievementFinal.json with ensure_ascii=False
        with open(r'JSON\Error.json', 'w', encoding='utf-8') as error_file:
            json.dump(game_error, error_file, indent=4, ensure_ascii=False)
    driver.quit()
    return info_game

def scroll_library(game_number, store_page, go_back):
    game_number +=1
    # Click store page
    pyautogui.click(store_page)
    time.sleep(2)
    # Click back to Library
    pyautogui.click(go_back)
    pyautogui.press('tab')
    pyautogui.press('down')
    print()
    print(f"> NEXT GAME.")
    time.sleep(3)

    return game_number

    
def process_game():

    # Define coordinate of buttons on Steam
    store_page = (1053, 489)
    game_url = (132, 78)
    go_back = (21, 46)
    
    # Define the region for checking "SUCCES" (x, y, width, height)
    check_region = (1580, 530, 315, 430)  # Define the region for checking "SUCCES"

    # Define the variations of "SUCCES" to check
    target_texts = ["SUCCES", "succés", "succes"]

    # Initiate game number
    game_number = 1
    error_list = []
    
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    last_game_name = setup_library(last_game_name="龙骑战歌")

    while True:

        game_id, current_game, have_page = get_game_url(store_page, game_url, go_back)
        print(f"Game {game_number}: {current_game}")

        if have_page == True:
            if check_success(target_texts, region=check_region):
                print("Success Detected!")
                is_find = compare_game_with_json(current_game)
                if is_find == False:
                    print("Game not in JSON LIST.")
                    info_page = check_steam_page(game_id, current_game, error_list)
                    if not ("Steam essaye d'en apprendre plus sur ce jeu" in info_page or "Fonctionnalités de profil limitées" in info_page):
                        if not info_page == "Error":
                            print("Game is not PL or SIL.")
                            add_game_to_collection()
                        else:
                            print("Game page error. Check Error.json")
                    else:
                        print("Game with PL or SIL from Steam page. Not added.")
                else:
                    print("Game in JSON list. Not added.")
            else:
                print("No success...")
            if last_game_name == current_game:
                break
        
        game_number = scroll_library(game_number, store_page, go_back)


# If the script is run directly, run the main process
if __name__ == "__main__":
    process_game()