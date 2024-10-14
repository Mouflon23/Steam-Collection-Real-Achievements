import requests

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

# Example usage
game_id = 701160  # Replace this with any valid game ID
game_name = get_game_name(game_id)
print(f"The name of the game with ID {game_id} is: {game_name}")
