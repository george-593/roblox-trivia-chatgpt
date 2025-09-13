import pyautogui, pytesseract
from keyboard import is_pressed
from time import sleep
from PIL import Image
from os import remove, getenv
from dotenv import load_dotenv
from openai import OpenAI

# Dotenv
load_dotenv()

# Example tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract' - from https://pypi.org/project/pytesseract/
pytesseract.pytesseract.tesseract_cmd = getenv("TESSERACT_CMD")
# openai.api_key = getenv("OPENAI_API_KEY")

client = OpenAI(api_key=getenv("OPENAI_API_KEY"))

# Position of the text to capture
# Four-integer tuple of the left, top, width, and height
position = ()


# Helper function to wait for a keypress
def waitForPress(key):
    while True:
        if is_pressed(key):
            return
        else:
            sleep(0.1)


# Get new positions if there is no saved pos
def newPos():
    # Get the positions from the user
    print("Press F10 when your mouse is in the top-left corner of the text to capture")
    waitForPress("F10")
    topLeft = pyautogui.position()
    sleep(0.1)

    print(
        "Press F10 when your mouse is in the bottom-right corner of the text to capture"
    )
    waitForPress("F10")
    bottomRight = pyautogui.position()

    # Calculate the width and height between the two points
    width = bottomRight[0] - topLeft[0]
    height = bottomRight[1] - topLeft[1]

    # Save the new position data to data.txt
    global position
    position = (topLeft[0], topLeft[1], width, height)
    with open("data/data.txt", "w") as f:
        f.writelines([f"{str(num)}\n" for num in position])
    print(f"Saved new position data: {position}")


# Check if there is saved positions from data.txt
try:
    with open("data/data.txt", "r") as f:
        l = f.read()
        if len(l) > 0:
            try:
                position = tuple([int(num) for num in l.splitlines()])
            except ValueError:
                print("Invalid data saved in data.txt")
                newPos()
            print(f"Retrieved saved position data: {position}")
        else:
            print("No saved data found in data.txt.")
            newPos()
except FileNotFoundError:
    newPos()

# Main loop
while True:
    print("Press F10 when you want to take a screenshot.")
    waitForPress("F10")
    img = pyautogui.screenshot(region=position)

    txt = pytesseract.image_to_string(img)
    txt = txt.strip().replace("\n", "")
    print(f"Got text from image:\n{txt}")

    print("Making ChatGPT Request")
    resp = client.responses.create(
        model="gpt-5-nano",
        instructions="You are a trivia answering system. Always respond with only the correct answer. Do not include explanations, punctuation, or extra text.",
        input=txt,
    )

    print(resp.output_text)
