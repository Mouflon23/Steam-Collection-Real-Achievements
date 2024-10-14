import pyautogui
import pytesseract
import json
import cv2
import numpy as np
import time
import os
import pyperclip
import requests

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
store_page = (1055, 487)
game_url = (90, 75)
go_back = (23, 45)

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
            
            # Click store page Point(x=1055, y=487)
            pyautogui.click(store_page)
            time.sleep(3)
            # Click game_page
            pyautogui.click(game_url)
            game_page = pyperclip.paste()
            # Click back to Library Point(x=90, y=75)
            time.sleep(1)
            pyautogui.click(go_back) 
            pyautogui.press('tab')  
            # Extract the game name
            game_id = game_page.split('/')[-3].replace('_', ' ')  # Get appID

            game_name_a = get_game_name(game_id)
            print("Game : ", game_name_a)
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