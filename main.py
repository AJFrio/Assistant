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
from firebase import Firebase

# Load environment variables from .env file
load_dotenv()
tools = funclist
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
name = "CAS-E"
id = "(Central Automated System - Epic)"
fb = Firebase()  # Create an instance of the Firebase class
fb.update_status("on")
computers = fb.get_all_computers()

# Define task handlers for Firebase polling
def handle_command_task(task_id, task_data):
    """Handle a command execution task"""
    print(f"Executing command: {task_data}")
    command = task_data.get('params', {}).get('command')
    if command:
        result = f.run_command(command)
        return {"command_result": result}
    return {"error": "No command provided"}

def handle_open_app_task(task_id, task_data):
    """Handle an open app task"""
    print(f"Opening app: {task_data}")
    app_name = task_data.get('params', {}).get('app_name')
    if app_name:
        result = f.focus_application(app_name)
        return {"app_opened": app_name}
    return {"error": "No app name provided"}

def handle_default_task(task_id, task_data):
    """Default handler for unrecognized tasks"""
    print(f"Received unhandled task type: {task_data.get('type')}")
    print(f"Task data: {task_data}")
    return {"status": "acknowledged"}

# Register task handlers
fb.register_task_handler("command", handle_command_task)
fb.register_task_handler("open_app", handle_open_app_task)

# Start task polling in the background
fb.start_task_polling(interval=30, default_handler=handle_default_task)

systemPrompt = f'''
    You are virtual assistant called {name} {id} developed by AJ Frio.
    \n
    You will be given a set of tools to use to complete the task. Only use a tool if it is apporpriate for the requested task. If required, you will also be given an image for context.
    If callinng any of the following tools, only call one, never stack these tools: 
    - send_message
    - open_app
    - check_email
    - get_info
    - send_email
    - check_jira
    - use_cursor
    \n
    Keep all responses short and direct.
    If the user asks for a task that is required to be completed by another computer, use the add_task_to_computer tool.
    Here are the availabe computers: {computers}
'''

greetings = [
    "Hello AJ",
    "Hi AJ",
    "Welcome back AJ",
    "How can I help you today AJ",
    "Meoooooowwww"
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
        self.root.title(id)
        self.root.geometry("1000x600")
        
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

        #Start it :)
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
                self.display_message(f"{name}: Listening...")
                audio = self.recognizer.listen(source)
                try:
                    user_input = self.recognizer.recognize_google(audio)
                    self.display_message(f"You (voice): {user_input}")
                except sr.UnknownValueError:
                    self.display_message(f"{name}: Sorry, I did not understand that.")
                    return
                except sr.RequestError:
                    self.display_message(f"{name}: Sorry, there was an error with the speech recognition service.")
                    return
        else:
            # Use text input
            user_input = self.input_field.get()
            if not user_input:
                return
            self.display_message(f"You: {user_input}")
            self.input_field.delete(0, tk.END)

        self.display_message(f"{name}: Generating...")
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
                    self.display_message(f"{name}: Message to {args['person']}: {args['message']}")
                ),
                "open_app": lambda args: (
                    f.focus_application(args['app_name']),
                    self.display_message(f"\n{name}: Opened {args['app_name']}")
                ),
                "check_email": lambda args: (
                    self.display_message(f"\n{name}: {f.check_email()}")
                ),
                "get_info": lambda args: (
                    self.display_message(f"\n{name}: {f.get_info(args['input'])}")
                ),
                "send_email": lambda args: (
                    f.send_email(args['people'], args['cc'], args['subject'], args['message']),
                    self.display_message(f"\n{name}: Email sent to {args['people']} with subject {args['subject']}")
                ),
                "check_jira": lambda args: (
                    self.display_message(f"\n{name}: {f.check_jira()}")
                ),
                "use_cursor": lambda args: (
                    f.use_cursor(args['prompt']),
                    self.display_message(f"\n{name}: Cursor request sent")
                ),
                "check_website": lambda args: (
                    self.chat_history.append({"role": "assistant", "content": f.check_website(args['url'], args['context'])}),
                    self.display_message(f"\n{name}: {f.check_website(args['url'], args['context'])}")
                ),
                "run_command": lambda args: (
                    f.run_command(args['command']),
                    self.display_message(f"\n{name}: Command run: {args['command']}")
                ),
                'add_task_to_computer': lambda args: (
                    fb.add_task_to_computer(args['target_computer'], args['task_type'], args['task_params']),
                    self.display_message(f"\n{name}: Task added to {args['target_computer']}")
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
            self.display_message(f"\n{name}: {response.choices[0].message.content}")
            self.chat_history.append({"role": "assistant", "content": response.choices[0].message.content})


def main():
    root = tk.Tk()
    app = AssistantGUI(root)
    root.mainloop()
    # Stop polling and update status when the application exits
    fb.stop_task_polling()
    fb.update_status("off")

if __name__ == "__main__":
    main()
