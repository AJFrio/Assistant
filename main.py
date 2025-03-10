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
    -Cursor: VS Code based IDE with AI built-in
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
    chat_history = []

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

        self.display_message("Gerald: Hello")

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
                self.display_message("Gerald: Listening...")
                audio = self.recognizer.listen(source)
                try:
                    user_input = self.recognizer.recognize_google(audio)
                    self.display_message(f"You (voice): {user_input}")
                except sr.UnknownValueError:
                    self.display_message("Gerald: Sorry, I did not understand that.")
                    return
                except sr.RequestError:
                    self.display_message("Gerald: Sorry, there was an error with the speech recognition service.")
                    return
        else:
            # Use text input
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
            tool_call = response.choices[0].message.tool_calls[0]
            self.chat_history.append({"role": "assistant", "content": response.choices[0].message.tool_calls[0].function.name})
            args = json.loads(tool_call.function.arguments)
            if tool_call.function.name == "send_message":
                f.send_message(args['message'], args['person'])
                self.display_message(f"Gerald: Message to {args['person']}: {args['message']}")
            elif tool_call.function.name == "open_app":
                f.focus_application(args['app_name'])
                self.display_message(f"\nGerald: Opened {args['app_name']}")
            elif tool_call.function.name == "check_email":
                emails = f.check_email()
                self.display_message(f"\nGerald: {emails}")
            elif tool_call.function.name == "get_info":
                info = f.get_info(args['input'])
                self.display_message(f"\nGerald: {info}")
            elif tool_call.function.name == "send_email":
                f.send_email(args['people'], args['cc'], args['subject'], args['message'])
                self.display_message(f"\nGerald: Email sent to {args['people']} with subject {args['subject']}")
            elif tool_call.function.name == "check_jira":
                jira = f.check_jira()
                self.display_message(f"\nGerald: {jira}")
            elif tool_call.function.name == "use_cursor":
                f.use_cursor(args['prompt'])
                self.display_message("\nGerald: Cursor request sent")
            elif tool_call.function.name == "check_website":
                website = f.check_website(args['url'], args['context'])
                self.chat_history.append({"role": "assistant", "content": website})
                self.display_message(f"\nGerald: {website}")
        else:
            self.display_message(f"Gerald: {response.choices[0].message.content}")
            self.chat_history.append({"role": "assistant", "content": response.choices[0].message.content})


def main():
    root = tk.Tk()
    app = AssistantGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
