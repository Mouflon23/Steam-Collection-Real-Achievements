import pyautogui
import pytesseract
import json
import cv2
import numpy as np
import time
import os

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def get_text(text_region):
    # Take a screenshot of the specified text region
    screenshot = pyautogui.screenshot(region=text_region)
    text_img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    text_gray = cv2.cvtColor(text_img, cv2.COLOR_BGR2GRAY)

    # Specify the languages you want to use
    languages = 'eng+fr'  # Add more language codes as needed

    # Extract text from the image
    extracted_text = pytesseract.image_to_string(text_gray, lang=languages)
    return extracted_text


text_region = (45, 150, 776, 850)

game_name = get_text(text_region)
all_games = []
# Append the game name to the list of all games
all_games.append(game_name)

# Step 1: Clean up the game names by splitting at newline characters and removing empty entries
game_names_list = [name.strip() for name in all_games[0].split('\n') if name.strip()]

# Step 3: Count the number of games
total_games = len(game_names_list)

# Step 4: Print the sorted list and the total count
print(f"Sorted Game Names: {game_names_list}")
print(f"Total Number of Games: {total_games}")

# # Base region definition for the first game (Game 1)
# width = 900    # Width of the region
# height = 20    # Height of the region


# for j in range(30):
#     # Calculate the y-coordinate for Game 1 in this repeat
#     current_y = 208 + (j * 24)  # Start with Game 1 y-coordinate
#     # Define the current check_region
#     text_region = (45, current_y, width, height)
#     time.sleep(2)

#     game_name = get_text(text_region)
#     print(f"Game Name: {game_name}")

#     # Press the Down Arrow key to scroll down
#     pyautogui.press('down')
#     print("NEXT GAME")

    #913 776