import pyautogui
import time
import os
from dotenv import load_dotenv
import openai
import base64
from io import BytesIO
import json
import tkinter as tk
from tkinter import ttk, scrolledtext
import pyperclip

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
    You are virtual assistant used to help speed up typing related jobs and anwser questions about on screen content. You will be given as task along with an image for context. 

    If you are given a chat between two people, only respond with what you think the proper resonse to the chat would be. Keep responses short and direct.
    If you are given a document, respond with what the task directed you to do based off the context of the file.

    In every response, you have to call one of the two tools.

    Respond only with the proper response for the situation.
'''

def typeText(text):
    pyperclip.copy(text)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.1)
    pyperclip.copy('')
    #pyautogui.write(text)

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

class AssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerald")
        self.root.geometry("600x400")
        
        # Configure dark theme colors
        self.root.configure(bg='#1a1a1a')  # Dark background
        
        style = ttk.Style()
        style.configure("Custom.TFrame", background="#212121")
        style.configure("Custom.TButton", 
                       padding=10,
                       font=('Helvetica', 10),
                       background="#000000",  # Dark button color
                       foreground="#000000")  # White text
        
        main_frame = ttk.Frame(root, padding="20", style="Custom.TFrame")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Chat display with dark theme
        self.chat_display = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            height=15,
            font=('Helvetica', 11),
            bg='#2f2f2f',  # Dark gray background
            fg='#ffffff',  # White text
            padx=10,
            pady=10,
            borderwidth=1,
            relief="solid"
        )
        self.chat_display.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))

        # Input field with dark theme
        self.input_field = ttk.Entry(
            main_frame,
            width=50,
            font=('Helvetica', 11),
            style="Custom.TEntry"
        )
        # Configure dark theme for input field
        style.configure("Custom.TEntry",
                       fieldbackground="#000000",
                       foreground="#000000",
                       insertcolor="#000000")  # Cursor color
        
        self.input_field.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=(0, 10), pady=10)

        # Send button with matching theme
        send_button = ttk.Button(
            main_frame,
            text="Send",
            command=self.process_input,
            style="Custom.TButton"
        )
        send_button.grid(row=1, column=1, sticky=(tk.E))

        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Bind enter key to process_input
        self.input_field.bind("<Return>", lambda e: self.process_input())

        self.display_message("Assistant: Hello! How can I help you today?")

    def display_message(self, message):
        self.chat_display.insert(tk.END, message + "\n")
        self.chat_display.see(tk.END)

    def process_input(self):
        user_input = self.input_field.get()
        if not user_input:
            return

        self.display_message(f"You: {user_input}")
        self.input_field.delete(0, tk.END)

        # Process with OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": systemPrompt},
                {"role": "user", 
                "content": [
                    {"type": "text", "text": user_input},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{getImage()}"}}
                ]}
            ],
            tools=tools
        )

        if not response.choices[0].message.content:
            tool_call = response.choices[0].message.tool_calls[0]
            args = json.loads(tool_call.function.arguments)
            if tool_call.function.name == "typeText":
                typeText(args['text'])
                self.display_message(f"Assistant: (Typed: {args['text']})")
            else:
                displayResponse(args['text'])
                self.display_message(f"Assistant: {args['text']}")
        else:
            self.display_message(f"Assistant: {response.choices[0].message.content}")

def main():
    root = tk.Tk()
    app = AssistantGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
