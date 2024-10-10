import requests

# URL of the SteamDB page
url = 'https://steamdb.info/tag/1003823/'

# Send a GET request to the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Save the HTML content to a file
    with open(r'Steam-Collection-Games-Success\HTML\PL.html', 'w', encoding='utf-8') as file:
        file.write(response.text)
    print("HTML page saved successfully.")
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
