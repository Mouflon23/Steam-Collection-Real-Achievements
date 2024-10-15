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

#SUCCES
#Point(x=1580, y=530)
#Point(x=1895, y=530)
#Point(x=1580, y=960)
#Point(x=1895, y=960)
# check_region = (1580, 530, 315, 430)  # Define the region for checking "SUCCES"

#Game 1
#Point(x=45, y=210)
#Point(x=45, y=230)
#Point(x=945, y=210)
#Point(x=945, y=230)
# check_region = (45, 210, 900, 20)  # Define the region for "Game 1"

#Game 2
#Point(x=45, y=235)
#Point(x=45, y=255)
#Point(x=945, y=235)
#Point(x=945, y=255)
# check_region = (45, 235, 900, 20)  # Define the region for "Game 2"