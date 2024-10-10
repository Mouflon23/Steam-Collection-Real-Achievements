import pyautogui
import pytesseract
import cv2
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

check_region = (45, 235, 904, 746)



# Take a screenshot of the specified text region
screenshot = pyautogui.screenshot(region=check_region)
text_img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
text_gray = cv2.cvtColor(text_img, cv2.COLOR_BGR2GRAY)

# Specify the languages you want to use
languages = 'eng+rus'  # Add more language codes as needed

# Extract text from the image
extracted_text = pytesseract.image_to_string(text_gray, lang=languages)
print(extracted_text)