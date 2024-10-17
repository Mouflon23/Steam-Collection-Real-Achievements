from GetPL_SILfromSteamdb import run_extraction_process
from AddGameToCollection import process_game
import os

def main():

    # Clearing the Screen
    os.system('cls')
    print("Starting process...")
    # getting info from Steamdb
    run_extraction_process()
    # add game to collection
    process_game()
    

if __name__ == "__main__":
    main()