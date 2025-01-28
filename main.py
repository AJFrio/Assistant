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
import functions as f
from funcList import funclist
from learn import ComputerUseAgent

# Load environment variables from .env file
load_dotenv()

tools = funclist

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

systemPrompt = '''
    You are virtual assistant developed by AJ used to help complete work tasks. IF required you will be given an image to help add context. 
    \n

    AJ is a web developer 1 at REP Fitness that specializes in web based 3D models.
    Here are a list of AJs general day to day tasks and tools he uses.
    \n

    Tasks:
    -Convert to CAD to web friendly format
    -Updates webpage with new 3D models
    -Other website related development tasks
    -Rendering 3D models for use in marketing materials
    \n

    Tools:
    -Bild PDM
    -Blender
    -Solidworks
    -Cursor: VS Code based IDE with AI builtin
    \n

    You will be given a set of tools to use to complete the task. Only use a tool if it is apporpriate for the requested task
    \n

    Keep all responses short and direct. Sound friendly, but not cheerful. Responses should be very monotone
    \n

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

        self.display_message("Gerald: Hello")

    def display_message(self, message):
        self.chat_display.insert(tk.END, message + "\n")
        self.chat_display.see(tk.END)

    def process_input(self):
        user_input = self.input_field.get()
        if not user_input:
            return

        self.display_message(f"You: {user_input}")
        self.input_field.delete(0, tk.END)
        
        self.display_message("Gerald: Generating...")
        self.root.update()

        # Check if image is needed based on keywords
        image_keywords = ['screen', 'see', 'look', 'show', 'image', 'pic', 'read', 'document', 'chat', 'ask', ]
        needs_image = any(keyword in user_input.lower() for keyword in image_keywords)
        if needs_image:
            print("Image needed")
        else:
            print("No image needed")

        # Prepare messages
        messages = [
            {"role": "system", "content": systemPrompt},
            {"role": "user", "content": user_input if not needs_image else [
                {"type": "text", "text": user_input},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{getImage()}"}}
            ]}
        ]

        # Process with OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools
        )

        # Remove the "Generating..." message
        self.chat_display.delete('end-2c linestart', 'end-1c lineend+1c')
        
        # Process response (rest of the code remains the same)
        if not response.choices[0].message.content:
            tool_call = response.choices[0].message.tool_calls[0]
            args = json.loads(tool_call.function.arguments)
            if tool_call.function.name == "send_message":
                f.send_message(args['message'], args['person'])
                self.display_message(f"\nGerald: Message to {args['person']}: {args['message']}")
            elif tool_call.function.name == "open_app":
                f.focus_application(args['app_name'])
                self.display_message(f"\nGerald: Opened {args['app_name']}")
            elif tool_call.function.name == "read_email":
                emails = f.read_email()
                self.display_message(f"\nGerald: {emails}")
            elif tool_call.function.name == "get_info":
                info = f.get_info(args['input'])
                self.display_message(f"\nGerald: {info}")
        else:
            self.display_message(f"\nGerald: {response.choices[0].message.content}")

def main():
    root = tk.Tk()
    app = AssistantGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
