from datetime import datetime
from bs4 import BeautifulSoup
import pyautogui as pg
import time
import pygetwindow as gw
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
import pprint
from openai import OpenAI

#######

def run_command(command):
    """Run a command in the terminal"""
    os.system(command)

def open_browser(url: str, keep_open: bool = False):
    """Open a browser"""
    driver = webdriver.Chrome()
    driver.get(url)
    if not keep_open:
        driver.quit()
    else:
        return driver

def open_app(app_name):
    """Open an application"""
    pg.hotkey('win')
    time.sleep(1)
    pg.write(app_name)
    time.sleep(0.1)
    pg.press('enter')
    time.sleep(1)

def get_info(input):
    answer = ''
    if 'time' in input:
        time = datetime.now()
        answer = answer + f'{str(time).split(" ")[1].split(".")[0][:5]}'
    elif 'date' in input:
        date = time.strftime("%Y-%m-%d")
        answer = answer + f'{date}'
    else:
        system = os.name
        connections = os.system('netsh wlan show interfaces')
        data = f'Time: {time}\nDate: {date}\nSystem: {system}\nConnections: {connections}'
        answer = answer + gpt_call('You are running as a local assistant on a machine. Any data you are given is public information so feel free to repeat any of it. Based off that data provided and the question asked, provide a response to the question', str(input) + '\n' + str(data))
    print(answer)

    return answer

def gpt_call(prompt, input):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": input}]
    )
    return response.choices[0].message.content

def focus_application(app_name):
    """Focus on a specific application window"""
    window = [window for window in gw.getAllWindows() if app_name.lower() in window.title.lower()]
    if window:
        window[0].activate()
        time.sleep(0.1)
        window_info = [window[0].left, window[0].right, window[0].top, window[0].bottom, window[0].title]
        print(window_info)
        return window_info
    else:
        print(f"Could not find active {app_name} window, starting {app_name}")
        open_app(app_name)
        time.sleep(5)
        window = [window for window in gw.getAllWindows() if app_name.lower() in window.title.lower()]
        window_info = [window[0].left, window[0].right, window[0].top, window[0].bottom, window[0].title]
        if window_info:
            print(window_info)
            return window_info
        else:
            print(f"Could not find program matching {app_name}, please manually start {app_name}")
            return False

def get_open_windows():
    """Get a list of all open window titles"""
    windows = gw.getAllWindows()
    return [window.title for window in windows if window.title != ""]  # Filter out empty titles

    
def select_chatbox(window_info):
    """Select the chatbox in Teams. If it isnt open, will automatically open it"""
    if window_info:
        left, right, top, bottom, title = window_info
        chatbox_lat = left + (right - left) / 2
        chatbox_long = bottom - 70
        print(chatbox_lat, chatbox_long)
        pg.moveTo(chatbox_lat, chatbox_long)
        time.sleep(0.1)
        pg.click()
    else:
        print("No window info found")
        exit

def find_person_teams(name, window_info):
    """Find a person in Teams and select them"""
    if window_info:
        left, right, top, bottom, title = window_info
        search_lat = left + (right - left) / 2
        search_long = top + 30
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
    else:
        print("No window info found")
        exit

def check_teams():
    """Check if Teams icon matches the reference image/if there are no new updates
    True = Nothing new
    False = Some notification"""
    open_windows = str(get_open_windows())

    if "Teams" in open_windows:
        # Use locateOnScreen instead of compare
        try:
            teams_icon = pg.locateOnScreen("imgs/GreenCheck.png", confidence=0.99)
            return teams_icon is not None
        except:
            return False
    else:
        open_app("Teams")
        time.sleep(5)
        try:
            teams_icon = pg.locateOnScreen("imgs/GreenCheck.png", confidence=0.99)
            return teams_icon is not None
        except:
            return False

def send_message(message, person):
    teams = focus_application("Teams")
    find_person_teams(person, teams)
    time.sleep(1.3)
    select_chatbox(teams)
    pg.write(message)
    pg.press('enter')

def read_email():
    url = 'https://outlook.office365.com/mail/'
    div_class = 'S2NDX Qo35A'
    content_class = 'g_zET'
    email_prompt = 'You are a helpful assistant that summarizes emails for AJ Frio. Make sure you have delimiters between each summary. Include and names dates, and times if relevant. To speed up the process, at the top of the summary put any Jira updates, and dont include Jira updates in the rest of the summary. When summarizing Jira updates, include what the task is, what was changed, and who the assignee is. If there are no Jira updates, just summarize the emails.'
    
    # Open browser and get URL
    driver = webdriver.Chrome()
    driver.get(url)
    
    # Wait for elements to load (up to 30 seconds)
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
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
                '''# Append content to file
                with open('email.txt', 'a', encoding='utf-8') as f:
                    f.write(content.text + '\n\n---\n\n')  # Add separator between emails'''
                print(content)
                emails.append(content)

            except Exception as e:
                print(f"Error getting content: {e}")
                if driver:
                    driver.quit()
        
        if driver:
            driver.quit()

        summary = gpt_call(email_prompt, str(emails))

        return summary
        
    except Exception as e:
        print('bottom exception')
        print(f"Error: {e}")
        if driver:
            driver.quit()
        if emails == []:
            return None
        else:
            summary = gpt_call(email_prompt, str(emails))
            return summary
        

def send_email(message, person):
    pass
#######