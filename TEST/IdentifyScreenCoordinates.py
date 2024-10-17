import pyautogui
import time

def get_item_position():
    # Get the current mouse position
    print("Move the mouse to the desired position in 3 seconds...")
    time.sleep(3)
    x, y = pyautogui.position()

    # Assign the position to a variable in the desired format
    value = (x, y)
    return value

item = get_item_position()
print(item)

# search bar (87, 184)