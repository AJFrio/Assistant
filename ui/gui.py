"""
GUI module for the Assistant application.
Implements the graphical user interface using Tkinter.
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Optional, Dict, Any, List, Callable
import time
import threading
import random
import json
import pyperclip

from core.logging import get_logger
from core.config import config
from api.openai import openai_client
from tasks.types import TASK_DEFINITIONS
from tasks.processor import task_processor

# Configure logger
logger = get_logger(__name__)


class AssistantGUI:
    """Main GUI class for the Assistant application."""
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the GUI
        
        Args:
            root (tk.Tk): Root Tkinter window
        """
        self.root = root
        self.root.title(f"{config.get('ASSISTANT_NAME')} {config.get('ASSISTANT_ID')}")
        self.root.geometry("1000x600")
        self.chat_history = []
        
        # Configure dark theme colors
        self._configure_theme()
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="20", style="Custom.TFrame")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Create chat display
        self._create_chat_display(main_frame)
        
        # Create input field and send button
        self._create_input_controls(main_frame)
        
        # Add voice mode checkbox
        self._create_settings_controls(main_frame)
        
        # Configure event bindings
        self._configure_events()
        
        # Display greeting
        self._display_greeting()
    
    def _configure_theme(self) -> None:
        """Configure the theme and styling for the GUI."""
        # Configure dark theme colors
        self.root.configure(bg='#1a1a1a')  # Dark background
        
        # Configure style
        style = ttk.Style()
        style.configure("Custom.TFrame", background="#212121")
        style.configure("Custom.TButton", 
                       padding=10,
                       font=('Helvetica', 10),
                       background="#424242",
                       foreground="#ffffff")
        
        # Configure input field style
        style.configure("Custom.TEntry",
                       fieldbackground="#2f2f2f",
                       foreground="#000000",
                       insertcolor="#ffffff")
        
        # Configure checkbox style
        style.configure("Custom.TCheckbutton",
                       background="#212121",
                       foreground="#ffffff")
        style.map("Custom.TCheckbutton",
                 background=[("active", "#323232")],
                 foreground=[("active", "#ffffff")])
    
    def _create_chat_display(self, parent: ttk.Frame) -> None:
        """
        Create the chat display area
        
        Args:
            parent (ttk.Frame): Parent frame
        """
        self.chat_display = scrolledtext.ScrolledText(
            parent,
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
        self.chat_display.config(state=tk.DISABLED)  # Make read-only
    
    def _create_input_controls(self, parent: ttk.Frame) -> None:
        """
        Create input field and send button
        
        Args:
            parent (ttk.Frame): Parent frame
        """
        # Input field
        self.input_field = ttk.Entry(
            parent,
            width=50,
            font=('Helvetica', 11),
            style="Custom.TEntry"
        )
        self.input_field.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=(0, 10), pady=10)
        
        # Send button
        send_button = ttk.Button(
            parent,
            text="Send",
            command=self.process_input,
            style="Custom.TButton"
        )
        send_button.grid(row=1, column=1, sticky=(tk.E), pady=10)
    
    def _create_settings_controls(self, parent: ttk.Frame) -> None:
        """
        Create settings controls
        
        Args:
            parent (ttk.Frame): Parent frame
        """
        # Voice mode checkbox
        self.voice_mode_var = tk.BooleanVar()
        voice_mode_checkbox = ttk.Checkbutton(
            parent,
            text="Voice Mode",
            variable=self.voice_mode_var,
            style="Custom.TCheckbutton"
        )
        voice_mode_checkbox.grid(row=2, column=0, sticky=(tk.W), pady=(0, 10))
    
    def _configure_events(self) -> None:
        """Configure event bindings."""
        # Bind Enter key to process input
        self.input_field.bind("<Return>", lambda event: self.process_input())
        
        # Bind Ctrl+C to copy selected text
        self.chat_display.bind("<Control-c>", self._copy_selected_text)
    
    def _copy_selected_text(self, event) -> None:
        """
        Copy selected text to clipboard
        
        Args:
            event: Event data
        """
        try:
            selected_text = self.chat_display.selection_get()
            pyperclip.copy(selected_text)
        except:
            pass  # No selection
    
    def _display_greeting(self) -> None:
        """Display a random greeting message."""
        greetings = [
            "Hello! How can I help you today?",
            "Hi there! What can I do for you?",
            "Welcome! I'm here to assist you.",
            "Hello! Ready when you are.",
            "Greetings! How may I assist you today?"
        ]
        greeting = random.choice(greetings)
        self.display_message(greeting, is_user=False)
    
    def display_message(self, message: str, is_user: bool = True) -> None:
        """
        Display a message in the chat display
        
        Args:
            message (str): Message to display
            is_user (bool): Whether the message is from the user
        """
        # Save message to history
        self.chat_history.append({
            "role": "user" if is_user else "assistant",
            "content": message
        })
        
        # Format message
        prefix = "You: " if is_user else f"{config.get('ASSISTANT_NAME')}: "
        formatted_message = f"{prefix}{message}\n\n"
        
        # Display message
        self.chat_display.config(state=tk.NORMAL)
        
        # Set text color based on role
        tag_name = "user" if is_user else "assistant"
        self.chat_display.tag_config("user", foreground="#ffffff")
        self.chat_display.tag_config("assistant", foreground="#ffffff")
        
        # Insert message
        self.chat_display.insert(tk.END, formatted_message, tag_name)
        self.chat_display.see(tk.END)  # Scroll to end
        self.chat_display.config(state=tk.DISABLED)
    
    def process_input(self) -> None:
        """Process user input and generate response."""
        # Get input text
        user_input = self.input_field.get().strip()
        if not user_input:
            return  # Ignore empty input
        
        # Display user message
        self.display_message(user_input, is_user=True)
        
        # Clear input field
        self.input_field.delete(0, tk.END)
        
        # Process input in a separate thread
        threading.Thread(
            target=self._process_input_async,
            args=(user_input,),
            daemon=True
        ).start()
    
    def _process_input_async(self, user_input: str) -> None:
        """
        Process user input asynchronously
        
        Args:
            user_input (str): User input text
        """
        try:
            # Generate system prompt
            system_prompt = self._generate_system_prompt()
            
            # Generate response using OpenAI
            response = openai_client.generate_with_function_calling(
                system_message=system_prompt,
                user_message=user_input,
                tools=TASK_DEFINITIONS
            )
            
            # Process the response
            if response.get("tool_calls"):
                # Function call response
                tool_calls = response["tool_calls"]
                
                # Extract the first function call
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    # Create a task for the function call
                    task_id = f"task_{int(time.time() * 1000)}"
                    task_processor.add_task(task_id, function_name, function_args)
                    
                    # Display assistant response about the action
                    response_text = f"I'll {function_name.replace('_', ' ')} for you."
                    self.display_message(response_text, is_user=False)
                    
                    # TODO: Wait for task completion and display result
                    # This is a placeholder for actual result processing
                    # In a real implementation, you would poll for task completion
                    
            else:
                # Text response
                response_text = response.get("content", "I'm not sure how to respond to that.")
                self.display_message(response_text, is_user=False)
                
        except Exception as e:
            logger.error(f"Error processing input: {str(e)}")
            self.display_message(f"Sorry, an error occurred: {str(e)}", is_user=False)
    
    def _generate_system_prompt(self) -> str:
        """
        Generate the system prompt for the AI
        
        Returns:
            str: System prompt
        """
        computers = []  # In real implementation, get available computers
        
        system_prompt = f"""
        You are virtual assistant called {config.get('ASSISTANT_NAME')} {config.get('ASSISTANT_ID')} developed by AJ Frio.
        
        You will be given a set of tools to use to complete the task. Only use a tool if it is appropriate for the requested task.
        If calling any of the following tools, only call one, never stack these tools: 
        - send_message
        - open_app
        - check_email
        - get_info
        - send_email
        - check_jira
        - use_cursor
        
        Keep all responses short and direct.
        If the user asks for a task that is required to be completed by another computer, use the add_task_to_computer tool.
        Here are the available computers: {', '.join(computers) if computers else 'None configured'}
        """
        
        return system_prompt.strip()


# Function to create and start the GUI
def create_gui() -> AssistantGUI:
    """
    Create and start the GUI
    
    Returns:
        AssistantGUI: GUI instance
    """
    root = tk.Tk()
    gui = AssistantGUI(root)
    
    # Start task processor
    task_processor.start_processing()
    
    return gui


# Function to run the GUI
def run_gui(gui: AssistantGUI) -> None:
    """
    Run the GUI main loop
    
    Args:
        gui (AssistantGUI): GUI instance
    """
    try:
        gui.root.mainloop()
    finally:
        # Stop task processor when GUI is closed
        task_processor.stop_processing() 