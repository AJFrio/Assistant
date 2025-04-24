"""
Application automation utilities for the Assistant application.
Handles interactions with desktop applications via GUI automation.
"""
import time
import pyautogui as pg
import pygetwindow as gw
from typing import Optional, Dict, Any, List, Tuple, Union
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests

from core.logging import get_logger
from core.exceptions import AutomationError

# Configure logger
logger = get_logger(__name__)


def open_app(app_name: str) -> bool:
    """
    Open an application using the Windows Start menu
    
    Args:
        app_name (str): Name of the application to open
        
    Returns:
        bool: True if successful
        
    Raises:
        AutomationError: If the application could not be opened
    """
    try:
        logger.info(f"Opening application: {app_name}")
        pg.hotkey('win')
        time.sleep(1)
        pg.write(app_name)
        time.sleep(0.1)
        pg.press('enter')
        time.sleep(1)
        return True
    except Exception as e:
        logger.error(f"Error opening application: {str(e)}")
        raise AutomationError(f"Application open error", 
                            details={"app_name": app_name, "error": str(e)})


def get_open_windows() -> List[str]:
    """
    Get a list of all open window titles
    
    Returns:
        list: List of window titles
    """
    try:
        windows = gw.getAllWindows()
        return [window.title for window in windows if window.title != ""]  # Filter out empty titles
    except Exception as e:
        logger.error(f"Error getting open windows: {str(e)}")
        return []


def focus_application(app_name: str) -> Optional[List[Union[int, str]]]:
    """
    Focus on a specific application window
    
    Args:
        app_name (str): Name of the application to focus
        
    Returns:
        list or None: Window information [left, right, top, bottom, title] or None if not found
        
    Raises:
        AutomationError: If the application could not be focused after multiple attempts
    """
    try:
        logger.info(f"Focusing application: {app_name}")
        
        # Try to find the window
        window = [window for window in gw.getAllWindows() if app_name.lower() in window.title.lower()]
        
        if window:
            window[0].activate()
            time.sleep(0.1)
            window_info = [window[0].left, window[0].right, window[0].top, window[0].bottom, window[0].title]
            logger.info(f"Focused window: {window_info}")
            return window_info
        else:
            # Window not found, try to start the application
            logger.info(f"Could not find active {app_name} window, starting {app_name}")
            open_app(app_name)
            time.sleep(5)
            
            # Try again to find the window
            window = [window for window in gw.getAllWindows() if app_name.lower() in window.title.lower()]
            
            if window:
                window[0].activate()
                time.sleep(0.1)
                window_info = [window[0].left, window[0].right, window[0].top, window[0].bottom, window[0].title]
                logger.info(f"Focused window after starting: {window_info}")
                return window_info
            
            # Still not found
            error_msg = f"Could not find program matching {app_name}, please manually start {app_name}"
            logger.error(error_msg)
            raise AutomationError(error_msg)
            
    except Exception as e:
        if not isinstance(e, AutomationError):
            logger.error(f"Error focusing application: {str(e)}")
            raise AutomationError(f"Application focus error", 
                                details={"app_name": app_name, "error": str(e)})
        raise


def move_mouse(x: int, y: int, duration: float = 0.2) -> bool:
    """
    Move the mouse to specific coordinates
    
    Args:
        x (int): X coordinate
        y (int): Y coordinate
        duration (float): Duration of the movement in seconds
        
    Returns:
        bool: True if successful
    """
    try:
        pg.moveTo(x, y, duration=duration)
        return True
    except Exception as e:
        logger.error(f"Error moving mouse: {str(e)}")
        return False


def click(x: Optional[int] = None, y: Optional[int] = None, button: str = 'left', clicks: int = 1) -> bool:
    """
    Click at the current or specified position
    
    Args:
        x (int, optional): X coordinate (current position if None)
        y (int, optional): Y coordinate (current position if None)
        button (str): Mouse button ('left', 'right', 'middle')
        clicks (int): Number of clicks
        
    Returns:
        bool: True if successful
    """
    try:
        if x is not None and y is not None:
            pg.click(x=x, y=y, button=button, clicks=clicks)
        else:
            pg.click(button=button, clicks=clicks)
        return True
    except Exception as e:
        logger.error(f"Error clicking: {str(e)}")
        return False


def type_text(text: str, interval: float = 0.01) -> bool:
    """
    Type text at the current cursor position
    
    Args:
        text (str): Text to type
        interval (float): Interval between keystrokes in seconds
        
    Returns:
        bool: True if successful
    """
    try:
        pg.write(text, interval=interval)
        return True
    except Exception as e:
        logger.error(f"Error typing text: {str(e)}")
        return False


def press_key(key: str) -> bool:
    """
    Press a key
    
    Args:
        key (str): Key to press
        
    Returns:
        bool: True if successful
    """
    try:
        pg.press(key)
        return True
    except Exception as e:
        logger.error(f"Error pressing key: {str(e)}")
        return False


def hotkey(*keys: str) -> bool:
    """
    Press a combination of keys
    
    Args:
        *keys (str): Keys to press together
        
    Returns:
        bool: True if successful
    """
    try:
        pg.hotkey(*keys)
        return True
    except Exception as e:
        logger.error(f"Error pressing hotkey: {str(e)}")
        return False


def take_screenshot() -> Optional[Dict[str, Any]]:
    """
    Take a screenshot of the entire screen
    
    Returns:
        dict or None: Screenshot information or None if failed
    """
    try:
        screenshot = pg.screenshot()
        return {
            "width": screenshot.width,
            "height": screenshot.height,
            "image": screenshot
        }
    except Exception as e:
        logger.error(f"Error taking screenshot: {str(e)}")
        return None 

def run_command(command: str) -> bool:
    """
    Run a command in the terminal
    
    Args:
        command (str): Command to run
        
    Returns:
        bool: True if successful
    """
    try:
        logger.info(f"Running command: {command}")
        focus_application('powershell')
        time.sleep(3)
        pg.write(command)
        pg.press('enter')
        return True
    except Exception as e:
        logger.error(f"Error running command: {str(e)}")
        return False

def open_browser(url: str, keep_open: bool = False) -> Optional[webdriver.Chrome]:
    """
    Open a browser with the specified URL
    
    Args:
        url (str): URL to open
        keep_open (bool): Whether to keep the browser open
        
    Returns:
        webdriver.Chrome or None: Browser driver if keep_open is True, otherwise None
    """
    try:
        logger.info(f"Opening browser with URL: {url}")
        driver = webdriver.Chrome()
        driver.get(url)
        if not keep_open:
            driver.quit()
            return None
        else:
            return driver
    except Exception as e:
        logger.error(f"Error opening browser: {str(e)}")
        return None

def select_chatbox(window_info: List[Union[int, str]]) -> bool:
    """
    Select the chatbox in Teams. If it isn't open, will automatically open it
    
    Args:
        window_info (list): Window information [left, right, top, bottom, title]
        
    Returns:
        bool: True if successful
    """
    try:
        if window_info:
            left, right, top, bottom, title = window_info
            chatbox_lat = left + (right - left) / 2
            chatbox_long = bottom - 70
            logger.info(f"Selecting chatbox at coordinates: {chatbox_lat}, {chatbox_long}")
            pg.moveTo(chatbox_lat, chatbox_long)
            time.sleep(0.1)
            pg.click()
            return True
        else:
            logger.error("No window info found")
            return False
    except Exception as e:
        logger.error(f"Error selecting chatbox: {str(e)}")
        return False

def find_person_teams(name: str, window_info: List[Union[int, str]]) -> bool:
    """
    Find a person in Teams and select them
    
    Args:
        name (str): Name of the person to find
        window_info (list): Window information [left, right, top, bottom, title]
        
    Returns:
        bool: True if successful
    """
    try:
        if window_info:
            left, right, top, bottom, title = window_info
            search_lat = left + (right - left) / 2
            search_long = top + 30
            logger.info(f"Finding person in Teams: {name}")
            pg.moveTo(search_lat, search_long)
            time.sleep(0.1)
            pg.click()
            time.sleep(0.1)
            pg.write(name)
            time.sleep(.5)
            pg.press('down')
            time.sleep(0.3)
            pg.press('down')
            time.sleep(0.2)
            pg.press('enter')
            return True
        else:
            logger.error("No window info found")
            return False
    except Exception as e:
        logger.error(f"Error finding person in Teams: {str(e)}")
        return False

def check_teams() -> bool:
    """
    Check if Teams icon matches the reference image/if there are no new updates
    
    Returns:
        bool: True if no new notifications, False otherwise
    """
    try:
        logger.info("Checking Teams for new notifications")
        open_windows = str(get_open_windows())

        if "Teams" in open_windows:
            # Use locateOnScreen instead of compare
            try:
                teams_icon = pg.locateOnScreen("imgs/GreenCheck.png", confidence=0.99)
                return teams_icon is not None
            except Exception as e:
                logger.error(f"Error locating Teams icon: {str(e)}")
                return False
        else:
            open_app("Teams")
            time.sleep(5)
            try:
                teams_icon = pg.locateOnScreen("imgs/GreenCheck.png", confidence=0.99)
                return teams_icon is not None
            except Exception as e:
                logger.error(f"Error locating Teams icon after opening: {str(e)}")
                return False
    except Exception as e:
        logger.error(f"Error checking Teams: {str(e)}")
        return False

def send_message(message: str, person: str) -> bool:
    """
    Send a message to a person in Teams
    
    Args:
        message (str): Message to send
        person (str): Person to send the message to
        
    Returns:
        bool: True if successful
    """
    try:
        logger.info(f"Sending message to {person}: {message}")
        teams = focus_application("Teams")
        find_person_teams(person, teams)
        time.sleep(1.3)
        select_chatbox(teams)
        pg.write(message)
        pg.press('enter')
        return True
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        return False

def check_email() -> Optional[str]:
    """
    Check email in Outlook web and summarize
    
    Returns:
        str or None: Summary of emails, or None if no emails or error
    """
    try:
        logger.info("Checking email")
        url = 'https://outlook.office365.com/mail/'
        div_class = 'S2NDX Qo35A'
        content_class = 'g_zET'
        email_prompt = 'You are a helpful assistant that summarizes emails for AJ Frio. Make sure you have delimiters between each summary. Include and names dates, and times if relevant. To speed up the process, at the top of the summary put any Jira updates, and dont include Jira updates in the rest of the summary. When summarizing Jira updates, include what the task is, what was changed, and who the assignee is. If there are no Jira updates, just summarize the emails.'
        
        # Open browser and get URL
        driver = webdriver.Chrome()
        driver.get(url)
        
        emails = []
        
        try:
            # Wait for and find all elements with matching class
            elements = WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, div_class.replace(' ', '.')))
            )
            
            # Click each matching element and get content
            for element in elements:
                element.click()
                time.sleep(0.5)  # Small delay between clicks
                
                # Wait for and get content
                try:
                    content = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, content_class))
                    )
                    content = content.text
                    content = content.encode('ascii', 'ignore').decode('ascii')
                    logger.info(f"Email content found: {content[:100]}...")
                    emails.append(content)

                except Exception as e:
                    logger.error(f"Error getting content: {e}")
                    if driver:
                        driver.quit()
            
            if driver:
                driver.quit()

            # Note: gpt_call function is not being implemented here as it requires OpenAI setup
            # This would need to be implemented separately or modified to use a different approach
            # summary = gpt_call(email_prompt, str(emails))
            
            return str(emails)
            
        except Exception as e:
            logger.error(f"Error in email check process: {e}")
            if driver:
                driver.quit()
            if emails == []:
                return None
            else:
                # Same note about gpt_call as above
                # summary = gpt_call(email_prompt, str(emails))
                return str(emails)
    except Exception as e:
        logger.error(f"Error checking email: {str(e)}")
        return None

def send_email(to: list, cc: list, subject: str, message: str) -> bool:
    """
    Send an email using Outlook
    
    Args:
        to (list): List of recipients
        cc (list): List of CC recipients
        subject (str): Email subject
        message (str): Email message
        
    Returns:
        bool: True if successful
    """
    try:
        logger.info(f"Sending email with subject '{subject}' to {to}")
        outlook = focus_application('Outlook')
        left, right, top, bottom, title = outlook
        width = right - left
        height = bottom - top
        time.sleep(0.5)
        if width > 1243:
            pg.click(left + 140, top + 155)
        else:
            pg.click(left + 130, top + 220)
        time.sleep(0.5)
        for person in to:
            pg.write(person)
            time.sleep(1)
            pg.press('enter')
            time.sleep(0.5)
        pg.press('tab')
        time.sleep(0.5)
        if cc != []:
            for person in cc:
                pg.write(person)
                time.sleep(0.5)
                pg.press('enter')
                time.sleep(0.5)
        pg.press('tab')
        time.sleep(0.5)
        pg.write(subject)
        time.sleep(0.5)
        pg.press('tab')
        time.sleep(0.5)
        pg.write(message)
        time.sleep(0.5)
        pg.hotkey('ctrl', 'enter')  # Send the email
        return True
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False

def check_website(url: str, context: str = None) -> Optional[str]:
    """
    Check a website for specific content
    
    Args:
        url (str): URL to check
        context (str, optional): Context for content extraction
        
    Returns:
        str or None: Website content or None if error
    """
    try:
        logger.info(f"Checking website: {url}")
        response = requests.get(url)
        if response.status_code == 200:
            try:
                response_text = response.text
                logger.info(f"Website content retrieved: {len(response_text)} characters")
                return response_text
            except Exception as e:
                logger.error(f"Error parsing website content: {str(e)}")
                return None
        else:
            logger.error(f"Error accessing website: Status code {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error checking website: {str(e)}")
        return None

def check_files(general_file_name: str, general_file_path: str) -> Optional[List[str]]:
    """
    Check for files matching a pattern in a directory
    
    Args:
        general_file_name (str): Pattern to match file names
        general_file_path (str): Directory path to search
        
    Returns:
        list or None: List of matching files or None if error
    """
    try:
        logger.info(f"Checking for files matching '{general_file_name}' in {general_file_path}")
        matching_files = []
        if os.path.exists(general_file_path):
            for file in os.listdir(general_file_path):
                if general_file_name.lower() in file.lower():
                    matching_files.append(file)
            return matching_files
        else:
            logger.error(f"Directory does not exist: {general_file_path}")
            return None
    except Exception as e:
        logger.error(f"Error checking files: {str(e)}")
        return None 