import pyautogui
import pytesseract
import json
import cv2
import numpy as np
import time
import os

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def is_text_visible(region=None):
    # Take a screenshot
    screenshot = pyautogui.screenshot(region=region)
    
    # Convert the screenshot to a numpy array and to grayscale
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Use pytesseract to extract text
    extracted_text = pytesseract.image_to_string(gray_img)

    # Check if any of the target variations are in the extracted text
    return any(target_text.lower() in extracted_text for target_text in target_texts)

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

# Define the region for checking "SUCCES" (x, y, width, height)
check_region = (1580, 530, 315, 430)  # Define the region for checking "SUCCES"

# Define the variations of "SUCCES" to check
target_texts = ["SUCCES", "succés", "succes"]

# Pause for a moment to set up your screen
print("Click on top of games list...")
time.sleep(5)


# Region to capture names of game displayed
text_region = (45, 150, 776, 850)
# Initialize the list for games with achievements
games_with_achievements = []
# Now, we need to repeat the process 30 times
# Loop to define regions for 30 iterations starting from Game 1

while(True):

    game_name = get_text(text_region)
    games_displayed = []
    
    # Append the game name to the list of all games
    games_displayed.append(game_name)

    # Clean up the game names by splitting at newline characters and removing empty entries
    game_names_list = [name.strip() for name in games_displayed[0].split('\n') if name.strip()]
    # Count the number of games
    total_games = len(game_names_list)

    # Print the sorted list and the total count
    print(f"Sorted Game Names: {game_names_list}")
    print(f"Total Number of Games: {total_games}")

    for j in range(total_games):
        print(f'Game Name: {game_names_list[j]}')
        if is_text_visible(region=check_region):
            print("Success Detected!")
            game_name_a = game_names_list[j]
            # Add the game name to the list
            games_with_achievements.append(game_name_a)
            print("Game added to Achievement.json")

            # Save the games with achievements to a JSON file immediately
            output_file = r'JSON\Achievement.json'
            if os.path.exists(output_file):
                # Load the existing data if the file already exists
                with open(output_file, 'r') as file:
                    data = json.load(file)
            else:
                data = []

            # Append new games to the existing data
            data.append(game_name_a)

            # Write the updated data back to the JSON file
            with open(output_file, 'w') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

            print("Achievement.json updated with the new game.")

        # Press the Down Arrow key to scroll down
        pyautogui.press('down')
        print("NEXT GAME")
        time.sleep(3)
    # Check for exit conditions
    if "Zvezda" in game_names_list or "Zuria" in game_names_list:
        break

print("All Games with Achievements have been added to Achievement.json")