import pyautogui
import time
import json
import pyperclip
import pytesseract
import cv2
import numpy as np
import time
import os

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

games_not_found = False
search_bar = (64, 180)
game_name = (69, 245)
game_settings = (1789, 431)
add_to = (1705, 497)
collection_success = (1448, 699)
# Region to capture names of game displayed
text_region = (45, 230, 776, 700)
time_sleep = 2

with open(r'SteamDB Get All games with Success\JSON\AchievementFinal.json', 'r', encoding='utf-8') as achievement_file:
    achievement = json.load(achievement_file)

def format_seconds(seconds):
    days = seconds // 86400  # There are 86400 seconds in a day (24*60*60)
    seconds %= 86400         # Remaining seconds after extracting days
    hours = seconds // 3600  # There are 3600 seconds in an hour (60*60)
    seconds %= 3600          # Remaining seconds after extracting hours
    minutes = seconds // 60  # There are 60 seconds in a minute
    seconds %= 60            # Remaining seconds are the final seconds

    # Return formatted string in the form DAYS:HOURS:MINUTES:SECONDS
    return f"{days}:{hours:02}:{minutes:02}:{seconds:02}"

def get_text(text_region):
    # Take a screenshot of the specified text region
    screenshot = pyautogui.screenshot(region=text_region)
    # Define the path to save the screenshot
    screenshot_path = r'SteamDB Get All games with Success'

    text_img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    text_gray = cv2.cvtColor(text_img, cv2.COLOR_BGR2GRAY)
    # Apply thresholding
    _, adjusted = cv2.threshold(text_gray, 170, 255, cv2.THRESH_BINARY)
        # Specify the languages you want to use
    languages = 'eng+fr'  # Add more language codes as needed
    # Extract text from the image
    extracted_text = pytesseract.image_to_string(adjusted, lang=languages)
    return extracted_text

# Step 2: Log the number of values in the JSON
num_values = len(achievement)
print(f"Total games: {num_values}")
print(f"Time to add all games: {format(num_values*time_sleep*2)}")

for value in achievement:

    pyautogui.click(search_bar)
    pyautogui.hotkey('ctrl', 'a')
    pyperclip.copy(value)
    # type name game from AchievementFinal.json
    # Use pyautogui to paste the value (Ctrl+V)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(time_sleep)
    pyautogui.click(game_name)
    
    game_name_search = get_text(text_region)
    games_displayed = []
    # Append the game name to the list of all games
    games_displayed.append(game_name_search)
    game_names_list = [name.strip() for name in games_displayed[0].split('\n') if name.strip()]
    print(game_names_list)

    if value in game_names_list:
        # add game to collection
        pyautogui.click(game_settings)
        pyautogui.click(add_to)
        pyautogui.click(collection_success)
        print("Game added to collection")
        print('Next Game')
        time.sleep(time_sleep)
    
    else:
        games_not_found = True
        not_found = value
        with open(r'SteamDB Get All games with Success\JSON\NotFound.json', 'w') as not_found_file:
            json.dump(not_found, not_found_file, indent=4, ensure_ascii=False)
        print('Game not found. Game added to NotFound.json.')
        print('Next Game')

if games_not_found:
    print('All games added.')
    
else:
    print("Games added.")
    print("Check NotFound.json for games not found.")