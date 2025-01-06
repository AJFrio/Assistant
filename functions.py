import pyautogui
import time
import pygetwindow as gw
import os

def focus_application(app_name):
    """Focus on a specific application window"""
    try:
        window = gw.getWindowsWithTitle(app_name)[0]
        window.activate()
        return True
    except IndexError:
        print(f"Could not find window: {app_name}")
        return False

def get_open_windows():
    """Get a list of all open window titles"""
    windows = gw.getAllWindows()
    return [window.title for window in windows if window.title != ""]  # Filter out empty titles

def focus_teams_windows():
    """Find and bring forward any windows that have 'Teams' in their title
    Returns the window coordinates left, top, bottom, right"""
    teams_windows = [window for window in gw.getAllWindows() if 'Teams' in window.title]
    if teams_windows:
        for window in teams_windows:
            try:
                window.activate()
                time.sleep(0.1)  # Small delay to allow window to come forward
            except Exception as e:
                print(f"Error focusing Teams window: {window.title} - {str(e)}")
        return [window.left, window.top, window.bottom, window.right]
    else:
        print("No Teams windows found")
        return False
    
def select_chatbox():
    if "Teams" in str(get_open_windows()):
        teams_windows = focus_teams_windows()
        print(teams_windows)
        left, top, bottom, right = teams_windows
        chatbox_lat = left + (right - left) / 2
        chatbox_long = bottom - 50
        print(chatbox_lat, chatbox_long)
        pyautogui.moveTo(chatbox_lat, chatbox_long)
        time.sleep(0.1)
        pyautogui.click()
    else:
        open_app("Teams")
        time.sleep(5)
        teams_windows = focus_teams_windows()
        print(teams_windows)
        left, top, bottom, right = teams_windows
        chatbox_lat = left + (right - left) / 2
        chatbox_long = bottom - 50
        print(chatbox_lat, chatbox_long)
        pyautogui.moveTo(chatbox_lat, chatbox_long)
        time.sleep(0.1)
        pyautogui.click()
        

def run_command(command):
    """Run a command in the terminal"""
    os.system(command)

def open_app(app_name):
    """Open an application"""
    pyautogui.hotkey('win')
    time.sleep(1)
    pyautogui.write(app_name)
    time.sleep(0.1)
    pyautogui.press('enter')
    time.sleep(1)

def check_teams():
    """Check if Teams icon matches the reference image/if there are no new updates
    True = Nothing new
    False = Some notification"""
    open_windows = str(get_open_windows())

    if "Teams" in open_windows:
        # Use locateOnScreen instead of compare
        try:
            teams_icon = pyautogui.locateOnScreen("imgs/GreenCheck.png", confidence=0.99)
            return teams_icon is not None
        except:
            return False
    else:
        open_app("Teams")
        time.sleep(5)
        try:
            teams_icon = pyautogui.locateOnScreen("imgs/GreenCheck.png", confidence=0.99)
            return teams_icon is not None
        except:
            return False

#print(get_open_windows())
print(check_teams())