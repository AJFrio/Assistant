import pyautogui
import time
import os
from dotenv import load_dotenv
import openai
import base64
from io import BytesIO
import json

# Load environment variables from .env file
load_dotenv()

tools = [
    {
        "type": "function",
        "function": {
            "name": "typeText",
            "description": "Used to type out text as an alternative to the keyboard",
            "parameters": {
                "type": "object", 
                "properties": {
                    "text": {
                        "type": "string", 
                        "description": "The text to type out"
                    }
                }, 
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "displayResponse",
            "description": "Used to display a response to the user",
            "parameters": {
                "type": "object", "properties": {"text": {"type": "string", "description": "The text to display"}}, "required": ["text"]}
        }
    }
]

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

systemPrompt = '''
    You are virtual assistant used to help speed up typing related jobs. You will be given as task along with an image for context. 

    If you are given a chat between two people, only respond with what you think the proper resonse to the chat would be. Keep responses short and direct.
    If you are given a document, respond with what the task directed you to do based off the context of the file.

    In every response, you have to call one of the two tools.

    Respond only with the proper response for the situation.
'''

def typeText(text):
    pyautogui.write(text)

def displayResponse(text):
    print(text)

def getImage():
    # Take screenshot
    image = pyautogui.screenshot()
    
    # Convert to base64
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return img_str

print('Hello')
while True:
    task = input()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are virtual assistant used to help speed up typing related jobs. You will be given as task along with an image for context. If you are given a chat between two people, only respond with what you think the proper resonse to the chat would be. Keep responses short and direct. Respond only with the proper response for the situation."}, 
            {"role": "user", 
            "content": [
                {"type": "text", "text": task},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{getImage()}"}}
            ]}
        ],
        tools=tools
    )

    if not response.choices[0].message.content:
        tool_call = response.choices[0].message.tool_calls[0]
        args = json.loads(tool_call.function.arguments)
        typeText(args['text'])
    else:
        displayResponse(response.choices[0].message.content)
