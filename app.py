import pyautogui, pytesseract, pyperclip, re, json
from keyboard import is_pressed
from time import sleep
from os import getenv
from dotenv import load_dotenv
from openai import OpenAI

import config

# Dotenv
load_dotenv()

# Example tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract' - from https://pypi.org/project/pytesseract/
pytesseract.pytesseract.tesseract_cmd = getenv("TESSERACT_CMD")

client = OpenAI(api_key=getenv("OPENAI_API_KEY"))

# Position of the text to capture
# Four-integer tuple of the left, top, width, and height
position = ()
prompt = ""


# Helper function to wait for a keypress
def waitForPress(key):
    while True:
        if is_pressed(key):
            return
        else:
            sleep(0.1)


# Load saved config data
try:
    with open("data/config.json", "r") as f:
        data = json.load(f)
        gameNames = list(data["games"].keys())
        selected = input(
            f"Please select the game to load, Available options: {gameNames}\n"
        )

        try:
            game = data["games"][selected]
        except KeyError:
            print("Invalid game name.")
            exit()

        position = (game["x"], game["y"], game["width"], game["height"])
        print(position)
        prompt = game["prompt"]
except FileNotFoundError:
    print("No configuration found, entering config mode.")
    config.decideConfig()

# Main loop
while True:
    print("Press F10 when you want to take a screenshot.")
    waitForPress("F10")
    # Take screenshot and OCR the text from it
    img = pyautogui.screenshot(region=position)
    txt = pytesseract.image_to_string(img)

    # Strip extra whitespace/newlines and remove unnecessary text
    txt = txt.strip().replace("\n", " ")
    txt = re.sub(
        r"for \$?(200|400|600|800|1000)|bonus round", ":", txt, flags=re.IGNORECASE
    )
    print(f"Got text from image:\n{txt}")

    # Make a request to ChatGPT for the answer
    print("Making ChatGPT Request")
    resp = client.responses.create(
        model="gpt-5-nano",
        instructions=prompt,
        input=txt,
    )

    output = resp.output_text
    # Output response in bold and copy to clipboard
    print(f"\033[1m{output}\033[0m \nResponse copied to clipboard")
    pyperclip.copy(output)
