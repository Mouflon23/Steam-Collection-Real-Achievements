from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
from bs4 import BeautifulSoup
import os
import shutil

def delete_all_html_contents(directory):
    """
    Deletes all files and subdirectories in the specified directory.
    """
    try:
        # List all files and subdirectories in the directory
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                # Check if it's a file or directory
                if os.path.isfile(file_path):
                    os.remove(file_path)  # Delete file
                    print(f"Deleted file: {file_path}")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Delete directory and its contents
                    print(f"Deleted directory and its contents: {file_path}")
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
    except Exception as e:
        print(f"Error accessing directory {directory}. Reason: {e}")

def extract_links_to_json(input_html, output_json):
    """
    Function to extract all text links from <a> tags with a specific class and target, and save them to a JSON file.
    """
    with open(input_html, 'r', encoding='utf-8') as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'lxml')
    links = soup.find_all('a', class_='b', target='_blank')

    extracted_texts = [link.text for link in links]

    with open(output_json, 'w', encoding='utf-8') as json_file:
        json.dump(extracted_texts, json_file, ensure_ascii=False, indent=4)

    print(f"Extracted text content has been saved to {output_json}.")

def fetch_steamdb_html(url, output_html):
    """
    Function to automate the browser, select "All(slow)" in dropdown, and save the resulting HTML to a file.
    """
    chrome_options = Options()
    # Comment or remove the following line to disable headless mode
    # chrome_options.add_argument("--headless")  # Run headless browser if you don't need GUI
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    driver.get(url)
    
    time.sleep(5)  # Adjust this as necessary
    print("Wait for the page to load...")
    element_xpath = '//*[@id="dt-length-0"]'
    # Wait for the dropdown element to be present
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, element_xpath)))
    dropdown = driver.find_element(By.XPATH, element_xpath)
    select = Select(dropdown)
    select.select_by_value('-1')
    
    print("Option to show all games selected. Waiting for the page to load all games...")
    time.sleep(10)  # Adjust this as necessary

    html_content = driver.page_source

    with open(output_html, 'w', encoding='utf-8') as file:
        file.write(html_content)

    print(f"HTML page saved successfully to {output_html}.")
    
    driver.quit()

def run_extraction_process():
    """
    Main function to run the entire process of fetching HTML and extracting links to JSON files.
    """
    # URLs and file paths
    steamdb_url = 'https://steamdb.info/tag/1003823/'
    pl_html_path = r'HTML\PL.html'
    sil_html_path = r'HTML\SIL.html'
    pl_json_output = r'JSON\PL.json'
    sil_json_output = r'JSON\SIL.json'

    # Fetch and save HTML for the first URL
    fetch_steamdb_html(steamdb_url, pl_html_path)

    # Prompt user to manually download SIL.html after doing tasks in the browser
    print("Go to your browser.")
    print("Use this address => https://steamdb.info/sales/?category=777&min_discount=0&min_rating=0&min_reviews=0")
    print("Find the '*** entries per page' and use the option 'All (slow)'.")
    print("Ctrl+S and save the HTML file in the folder 'HTML' with the name 'SIL.html'.")
    input("Press Enter when previous task is done...")

    # Extract links to JSON for PL.html
    extract_links_to_json(pl_html_path, pl_json_output)

    # Extract links to JSON for SIL.html
    extract_links_to_json(sil_html_path, sil_json_output)

    # Delete all files and subdirectories in the HTML folder
    delete_all_html_contents(r'HTML')

# If the script is run directly, run the main process
if __name__ == "__main__":
    run_extraction_process()