import pyautogui, keyboard, json


def loadFile():
    try:
        # Try to open the file, will raise FileNotFoundError if the file doesn't exist
        f = open("data/config.json", "r+")
    except FileNotFoundError:
        # Create the file
        f = open("data/config.json", "w+")
    return f


def gameConfig():
    # Print current game info
    f = loadFile()
    # Try to load JSON, if not possible create new base config
    try:
        data = json.load(f)
        print(f"Current game data:\n{data['games']}")
    except json.JSONDecodeError:
        data = {"games": {}, "global": {}}
        print("Unable to load current config")

    # Get game related data
    gameName = input("Enter the name of the game: ")
    if gameName == "":
        print("Game name was not entered.")
        exit()

    gamePrompt = input(
        'Enter the prompt to be used for the game (Leave empty for: "Answer with only the correct trivia answer. Keep answers as short as possible.")'
    )
    if gamePrompt == "":
        gamePrompt = "Answer with only the correct trivia answer. Keep answers as short as possible."

    # Get the positions from the user
    print("Press F10 when your mouse is in the top-left corner of the text to capture")
    keyboard.wait("F10")
    topLeft = pyautogui.position()

    print(
        "Press F10 when your mouse is in the bottom-right corner of the text to capture"
    )
    keyboard.wait("F10")
    bottomRight = pyautogui.position()

    # Calculate the width and height between the two points
    width = bottomRight[0] - topLeft[0]
    height = bottomRight[1] - topLeft[1]

    data["games"][gameName] = {
        "prompt": gamePrompt,
        "x": topLeft[0],
        "y": topLeft[1],
        "width": width,
        "height": height,
    }
    # Close the file and re-open in write mode so we can clear previous data and overwrite with new data
    f.close()
    f = open("data/config.json", "w")
    json.dump(data, f)
    f.close()


def globalConfig():
    pass


def decideConfig():
    choice = input(
        "Would you like to configure global settings or game specific settings (global/games): "
    )

    if choice == "global":
        globalConfig()
    elif choice == "games":
        gameConfig()


if __name__ == "__main__":
    decideConfig()
