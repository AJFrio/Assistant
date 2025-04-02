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
import random

# Load environment variables from .env file
load_dotenv()

tools = funclist

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

systemPrompt = '''
    You are virtual assistant called CAS (Central Automated System) developed by AJ Frio.
    \n
    You will be given a set of tools to use to complete the task. Only use a tool if it is apporpriate for the requested task. If required, you will also be given an image for context.
    \n
    Keep all responses short and direct.
    \n
    Respond only with the proper response for the situation.
'''

greetings = [
    "Hello AJ",
    "Hi AJ",
    "Welcome back AJ",
    "How can I help you today AJ",
]

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
    chat_history = []

    def __init__(self, root):
        self.root = root
        self.root.title("CAS")
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

        # Add Voice Mode checkbox
        self.voice_mode_var = tk.BooleanVar()
        voice_mode_checkbox = ttk.Checkbutton(
            main_frame,
            text="Voice Mode",
            variable=self.voice_mode_var,
            style="Custom.TCheckbutton"
        )
        voice_mode_checkbox.grid(row=2, column=0, sticky=(tk.W), pady=(0, 10))

        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Bind enter key to process_input
        self.input_field.bind("<Return>", lambda e: self.process_input())

        self.display_message(random.choice(greetings))

    def display_message(self, message):
        self.chat_display.insert(tk.END, message + "\n\n")
        self.chat_display.see(tk.END)

    def process_input(self):
        if self.voice_mode_var.get() and os.system('echo %PROCESSOR_ARCHITECTURE%') != 'ARM64':
            import speech_recognition as sr
            # Initialize speech recognizer
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()

            # Use speech recognition to get input
            with self.microphone as source:
                self.display_message("CAS: Listening...")
                audio = self.recognizer.listen(source)
                try:
                    user_input = self.recognizer.recognize_google(audio)
                    self.display_message(f"You (voice): {user_input}")
                except sr.UnknownValueError:
                    self.display_message("CAS: Sorry, I did not understand that.")
                    return
                except sr.RequestError:
                    self.display_message("CAS: Sorry, there was an error with the speech recognition service.")
                    return
        else:
            # Use text input
            user_input = self.input_field.get()
            if not user_input:
                return
            self.display_message(f"You: {user_input}")
            self.input_field.delete(0, tk.END)

        self.display_message("CAS: Generating...")
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
            {"role": "system", "content": systemPrompt}
        ]
        
        # Add chat history
        messages.extend(self.chat_history)
        
        # Add current user message
        messages.append({
            "role": "user", 
            "content": user_input if not needs_image else [
                {"type": "text", "text": user_input},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{getImage()}"}}
            ]
        })

        self.chat_history.append({"role": "user", "content": user_input})

        # Process with OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools
        )
        
        # Remove the "Generating..." message (including the extra newlines)
        self.chat_display.delete('end-3c linestart', 'end')
        
        # Process response
        if not response.choices[0].message.content:
            # Define the function handlers dictionary
            tool_handlers = {
                "send_message": lambda args: (
                    f.send_message(args['message'], args['person']),
                    self.display_message(f"CAS: Message to {args['person']}: {args['message']}")
                ),
                "open_app": lambda args: (
                    f.focus_application(args['app_name']),
                    self.display_message(f"\nCAS: Opened {args['app_name']}")
                ),
                "check_email": lambda args: (
                    self.display_message(f"\nCAS: {f.check_email()}")
                ),
                "get_info": lambda args: (
                    self.display_message(f"\nCAS: {f.get_info(args['input'])}")
                ),
                "send_email": lambda args: (
                    f.send_email(args['people'], args['cc'], args['subject'], args['message']),
                    self.display_message(f"\nCAS: Email sent to {args['people']} with subject {args['subject']}")
                ),
                "check_jira": lambda args: (
                    self.display_message(f"\nCAS: {f.check_jira()}")
                ),
                "use_cursor": lambda args: (
                    f.use_cursor(args['prompt']),
                    self.display_message("\nCAS: Cursor request sent")
                ),
                "check_website": lambda args: (
                    self.chat_history.append({"role": "assistant", "content": f.check_website(args['url'], args['context'])}),
                    self.display_message(f"\nCAS: {f.check_website(args['url'], args['context'])}")
                )
            }

            # Handle all tool calls
            for tool_call in response.choices[0].message.tool_calls:
                self.chat_history.append({"role": "assistant", "content": tool_call.function.name})
                args = json.loads(tool_call.function.arguments)
                
                # Execute the appropriate handler
                if tool_call.function.name in tool_handlers:
                    tool_handlers[tool_call.function.name](args)
        else:
            self.display_message(f"CAS: {response.choices[0].message.content}")
            self.chat_history.append({"role": "assistant", "content": response.choices[0].message.content})


def main():
    root = tk.Tk()
    app = AssistantGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
