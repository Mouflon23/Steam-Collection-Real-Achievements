import cv2
import numpy as np
import pyautogui
# Désactiver le mécanisme de sécurité de PyAutoGUI
pyautogui.FAILSAFE = False

import json
import pytesseract
import requests
import pyperclip
import time
from useSelenium import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def read_json(file_path):

    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)
    
def write_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    
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

def get_game_url(store_page, game_url, go_back, game_list):
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
                time.sleep(2)
                pyautogui.click(go_back)
                pyautogui.press('tab')
                # Extract the game name
                game_id = game_page.split('/')[4]  # Get appID
                game_name = get_game_name(game_id)
                game_list.append(game_name)
                game_list_path = r'JSON\gamesList.json'
                write_json(game_list_path, game_list)
                break
            else:
                game_id = None
                game_name = None
                time.sleep(2)
                pyautogui.click(go_back)
                time.sleep(2)
                pyautogui.press('tab')
                # pyautogui.click(75, 453)
                # pyautogui.press('down')
                print("Game page does not exist!")
                break

    return game_id, game_name, have_page


    
def setup_library(last_game, first_game, store_page, go_back, game_url):
    
    print("Open Steam.")
    print("Scroll library to the end.")
    input("Then press Enter to continue.")
    # Click last game
    pyautogui.click(last_game)
    time.sleep(0.5)
    pyautogui.click(store_page)
    
    while True:
        time.sleep(2)
        # Click game_page
        pyautogui.click(game_url)
        game_page = pyperclip.paste()
        # Check if the game_page contains 'https://store.steampowered.com/?snr='
        if 'https://store.steampowered.com/?snr=' not in game_page:
            if game_page != "https://store.steampowered.com/":
                # Click back to Library
                time.sleep(1)
                pyautogui.click(go_back)
                pyautogui.press('tab')
                # Extract the game name
                game_id = game_page.split('/')[4]  # Get appID
                last_game_name = get_game_name(game_id)
                break
            else:
                game_id = None
                last_game_name = None
                pyautogui.click(go_back)
                pyautogui.press('tab')
                # pyautogui.click(75, 453)
                # pyautogui.press('down')
                print("Game page does not exist!")
                break
    print(f'Last game : {last_game_name}')
    print("Scroll to the top of library.")
    print("Open Collection NO CATEGORY.")
    input("Then press Enter to continue.")
    # Click first game
    pyautogui.click(first_game)
    time.sleep(0.5)
    # Click store page
    pyautogui.click(store_page)
    time.sleep(0.5)
    # click go back
    pyautogui.click(go_back)
    time.sleep(0.5)
    # Click first game
    pyautogui.click(first_game)
    time.sleep(0.5)
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
    # print(extracted_text)

    # Check if any of the target variations are in the extracted text
    return any(target_text.lower() in extracted_text for target_text in target_texts)

def add_game_to_collection(collection, name_collection):

    game_settings = (1789, 431)
    add_to = (1705, 497)
    click_away = (1475, 418)

    # add game to collection
    pyautogui.click(game_settings)
    time.sleep(0.5)
    pyautogui.click(add_to)
    time.sleep(0.5)
    pyautogui.click(collection)
    time.sleep(0.5)
    pyautogui.click(click_away)
    print("Game added to collection", name_collection)

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
        error_file_path = r'JSON\Error.json'
        write_json(error_file_path, error_list)
    driver.quit()
    return info_game

def scroll_library(game_number):
    game_number +=1
    time.sleep(3)
    first_game_collection = (180, 478)
    # Click next game
    pyautogui.click(first_game_collection)
    print()
    print(f"> NEXT GAME.")
    print()
    time.sleep(1)

    return game_number

    
def process_game():

    # Define coordinate of buttons on Steam
    store_page = (382, 482)
    game_url = (132, 78)
    go_back = (21, 46)
    collection_success = (1449, 767)
    collection_PL_SIL = (1496, 730)
    collection_no_success = (1461, 702)
    collection_no_info = (1548, 531)
    first_game_collection = (53, 479)
    last_game = (65, 962)
    previous_game = None
    same_game_count = 0
    
    
    # Define the region for checking "SUCCES" (x, y, width, height)
    check_region = (1370, 530, 315, 430)  # Define the region for checking "SUCCES"

    # Define the variations of "SUCCES" to check
    target_texts = ["SUCCES", "succés", "succes"]

    # Initiate game number
    game_number = 1
    error_list = []
    game_list = []
    games_added = []
    
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    last_game_name = setup_library(last_game, first_game_collection, store_page, go_back, game_url)

    while True:

        game_id, current_game, have_page = get_game_url(store_page, game_url, go_back, game_list)
        print(f"Game {game_number}: {current_game}")
        
        if same_game_count > 1:
            print("Error Stopping the process.")
            break
        if previous_game == current_game:
            same_game_count += 1
        else:
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
                                add_game_to_collection(collection_success, "success")
                                games_added.append(current_game)
                                added_game_list_path = r'JSON\gamesAdded.json'
                                write_json(added_game_list_path, games_added)
                            else:
                                print("Game page error. Check Error.json")
                                add_game_to_collection(collection_no_info, "no info")
                        else:
                            print("Game with PL or SIL from Steam page.")
                            add_game_to_collection(collection_PL_SIL, "PL/SIL")
                    else:
                        print("Game in JSON list.")
                        add_game_to_collection(collection_PL_SIL, "PL/SIL")
                else:
                    print("No success...")
                    add_game_to_collection(collection_no_success, "no success")
                    
                if last_game_name == current_game:
                    print("End of library. Stopping process..")
                    break
            else:
                add_game_to_collection(collection_no_info, "no info")
            
            game_number = scroll_library(game_number)
            previous_game = current_game

# If the script is run directly, run the main process
if __name__ == "__main__":
    process_game()