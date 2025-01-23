import pyautogui
import anthropic
import base64
from typing import List, Dict, Any, Optional
import logging
import json
import time
from PIL import Image
import io
import time
import dotenv
import os
import socket
from funcList import funclist

memory = []

name = socket.gethostname()

dotenv.load_dotenv()


class ComputerUseAgent:
    def __init__(self, api_key: str):
        self.prime = '***If using a web browser, close any popups or notifications.*** /n *** When navigating around the computer, try to use the builtin tools to open apps. If the tools dont provide the right actions, then use mouse and keyboard inputs*** /n ***After each step, take a screenshot and carefully evaluate if you have achieved the right outcome. Explicitly show your thinking: "I have evaluated step X..." If not correct, try again. Only when you confirm a step was executed correctly should you move on to the next one.***'
        self.client = anthropic.Anthropic(api_key=api_key)
        self.tools = [
            {
                "type": "computer_20241022",
                "name": "computer",
                "display_width_px": int(pyautogui.size()[0]),
                "display_height_px": int(pyautogui.size()[1]),
                "display_number": 1,
            },
            {
                "type": "text_editor_20241022", 
                "name": "str_replace_editor"
            },
            {
                "type": "bash_20241022",
                "name": "bash"
            }
        ]
        self.tools.extend(funclist)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def take_screenshot(self) -> Dict[str, Any]:
        """Take a screenshot and return it as a base64 encoded image"""
        try:
            screenshot = pyautogui.screenshot()
            buffered = io.BytesIO()
            screenshot.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            result = {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": img_str
                }
            }
            print(f"Screenshot taken")
            return result
        except Exception as e:
            self.logger.error(f"Screenshot error: {str(e)}")
            raise

    def execute_computer_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a computer action (mouse/keyboard)"""
        try:
            action_type = action.get("action")
            print(f"Executing computer action: {action}")
            
            if action_type == "left_click":
                pyautogui.click()
                time.sleep(0.5)  # Wait for click to register
                print(f"****LEFT CLICKED****")
            
            elif action_type == "double_click":
                pyautogui.doubleClick()
                time.sleep(0.5)  # Wait for click to register
                print(f"****DOUBLE CLICKED****")

            elif action_type == "right_click":
                pyautogui.rightClick()
                time.sleep(0.5)  # Wait for click to register
                print(f"****RIGHT CLICKED****")
                
            elif action_type == "type":
                text = action.get("text", "")
                pyautogui.write(text)
                time.sleep(0.1)  # Wait between keypresses
                
            elif action_type == "key":
                key = action.get("text", "")
                if key == 'Return':
                    pyautogui.press('enter')
                else:
                    pyautogui.press(key)
                time.sleep(0.1)
                
            elif action_type == "mouse_move":
                x, y = action.get("coordinate", [0, 0])[0], action.get("coordinate", [0, 0])[1]
                pyautogui.moveTo(x=x, y=y)
                time.sleep(0.1)
                print(f"Moved to {x}, {y}")

            elif action_type == "left_click_drag":
                x, y = action.get("coordinate", [0, 0])[0], action.get("coordinate", [0, 0])[1]
                pyautogui.dragTo(x=x, y=y, button='left')
                time.sleep(0.1)
                print(f"Dragged to {x}, {y}")
                
            # Take a screenshot after any action
            return self.take_screenshot()
            
        except Exception as e:
            self.logger.error(f"Action execution error: {str(e)}")
            raise

    def process_tool_use(self, tool_use: Any) -> Dict[str, Any]:
        """Process a tool use request from Claude"""
        try:
            self.logger.info(f"Processing tool use: {tool_use.name}")
            print(f"Processing tool use: {tool_use}")
            
            if tool_use.name == "computer":
                result = self.execute_computer_action(tool_use.input)
            else:
                raise ValueError(f"Unsupported tool: {tool_use.name}")
            if result['type'] == "image":
                print(f"Screenshot taken (second confirmation)")
            else:
                print(f"Tool use result: {result}")
            # Return the content of the tool result
            return {
                "content": [result]
            }
            
        except Exception as e:
            self.logger.error(f"Tool use error: {str(e)}")
            error_result = {
                "content": f"Error: {str(e)}",
                "is_error": True
            }
            print(f"Tool use error result: {error_result}")
            return error_result

    def run_agent_loop(self, user_input: str) -> str:
        """Run the agent loop to process user input and handle tool use"""
        messages = [{"role": "user", "content": self.prime + "\n\n" + user_input}]
        print(f"Initial messages: {json.dumps(messages, indent=2)}")
        
        while True:
            try:
                print("Sending request to Claude...")
                response = self.client.beta.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1024,
                    tools=self.tools,
                    messages=messages,
                    betas=["computer-use-2024-10-22"],
                )
                print(f"Received response from Claude: {response}")
                
                if response.stop_reason == "tool_use":
                    for content in response.content:
                        if content.type == "tool_use":
                            # Assistant message indicating tool use
                            tool_use_message = {
                                "role": "assistant",
                                "content": [
                                    {
                                        "type": "tool_use",
                                        "id": content.id,
                                        "name": content.name,
                                        "input": content.input
                                    }
                                ]
                            }
                            messages.append(tool_use_message)
                            
                            # Process the tool use
                            tool_result = self.process_tool_use(content)
                            
                            # Add tool result as a user message
                            messages.append({
                                "role": "user",
                                "content": [
                                    {
                                        "type": "tool_result",
                                        "tool_use_id": content.id,
                                        "content": tool_result["content"],
                                        "is_error": tool_result.get("is_error", False)
                                    }
                                ]
                            })
                            break
                else:
                    # Final response from Claude
                    return response.content[0].text
                    
            except Exception as e:
                self.logger.error(f"Agent loop error: {str(e)}")
                return f"An error occurred: {str(e)}"
            time.sleep(3.5)

def main():
    # Read API key from file
    api_key = os.getenv("ANTHROPIC_API_KEY")
        
    agent = ComputerUseAgent(api_key)
    
    # Example usage
    while True:
        user_input = input("Enter your request (or 'q' to exit): ")
        if user_input.lower() == 'q':
            break
            
        result = agent.run_agent_loop(user_input)
        print("\nClaude's response:", result)

if __name__ == "__main__":
    main()
