# Given URL
url = "https://store.steampowered.com/app/2731530/Karina_Katana/"

# Extract the game name
game_name = url.split('/')[-2]  # Get the second last element from the split

print(game_name)
