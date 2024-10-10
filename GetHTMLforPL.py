import requests

# URL of the SteamDB page
url = 'https://steamdb.info/tag/1003823/'

# Set headers to mimic a browser request more completely
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Send a GET request with headers
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Ensure the directory exists
    import os
    os.makedirs(r'Steam-Collection-Games-Success\HTML', exist_ok=True)

    # Save the HTML content to a file
    with open(r'Steam-Collection-Games-Success\HTML\PL.html', 'w', encoding='utf-8') as file:
        file.write(response.text)
    print("HTML page saved successfully.")
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
