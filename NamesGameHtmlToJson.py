import json
from bs4 import BeautifulSoup

def extract_links_to_json(input_html, output_json):
    # Load the HTML file
    with open(input_html, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse the HTML
    soup = BeautifulSoup(html_content, 'lxml')

    # Find all <a> tags with the specified class and target
    links = soup.find_all('a', class_='b', target='_blank')

    # Extract the text content into a list
    extracted_texts = [link.text for link in links]

    # Save the extracted text content to a JSON file
    with open(output_json, 'w', encoding='utf-8') as json_file:
        json.dump(extracted_texts, json_file, ensure_ascii=False, indent=4)

    print(f"Extracted text content has been saved to {output_json}.")

# Process PL.html
extract_links_to_json('Steam-Collection-Games-Success\HTML\PL.html', 'Steam-Collection-Games-Success\JSON\PL.json')

# Process SIL.html
extract_links_to_json('Steam-Collection-Games-Success\HTML\SIL.html', 'Steam-Collection-Games-Success\JSON\SIL.json')
