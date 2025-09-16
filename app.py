import pyautogui, pytesseract, pyperclip, re, json, ollama, keyboard
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

aiType = ""
localModel = ""
regex = r""


def useChatGPT(txt):
    # Make a request to ChatGPT for the answer
    print("Making ChatGPT Request")
    resp = client.responses.create(
        model="gpt-5-nano",
        instructions=prompt,
        input=txt,
    )
    return resp.output_text


def useLocalLLM(txt):
    resp = ollama.generate(model=localModel, prompt=f"{prompt}\n\nUser: {txt}")
    return resp.response.strip().replace("\n", " ")


# Load saved config data
try:
    with open("data/config.json", "r") as f:
        data = json.load(f)

        # Load game dataq
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
        prompt = game["prompt"]
        regex = game["regex"]

        # Load global data
        aiType = data["global"]["aiType"]
        localModel = data["global"]["localModel"]
except FileNotFoundError:
    print("No configuration found, entering config mode.")
    config.decideConfig()

# Main loop
while True:
    print("Press F10 when you want to take a screenshot.")
    keyboard.wait("F10")
    # Take screenshot and OCR the text from it
    img = pyautogui.screenshot(region=position)
    txt = pytesseract.image_to_string(img)

    # Strip extra whitespace/newlines and remove unnecessary text
    txt = txt.strip().replace("\n", " ")
    if regex:
        txt = re.sub(regex, txt, flags=re.IGNORECASE)
    print(f"Got text from image:\n{txt}")

    if aiType == "local":
        output = useLocalLLM(txt)
    else:
        output = useChatGPT(txt)

    # Output response in bold and copy to clipboard
    print(f"\033[1m{output}\033[0m \nResponse copied to clipboard")
    pyperclip.copy(output)
