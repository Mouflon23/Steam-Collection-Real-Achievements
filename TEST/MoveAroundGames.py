import pyautogui
import time

# Pause for a moment to set up your screen
time.sleep(3)

# Press the Down Arrow key to scroll down
pyautogui.press('down')

check_region = (45, 210, 900, 20)  # Define the region for "Game 1"
# + 25
check_region = (45, 235, 900, 20)  # Define the region for "Game 2"
# + 25
check_region = (45, 260, 900, 20)  # Define the region for "Game 3"