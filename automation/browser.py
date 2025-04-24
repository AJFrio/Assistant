"""
Browser automation utilities for the Assistant application.
Handles interactions with web browsers using Selenium.
"""
import time
from typing import Dict, Any, List, Optional, Union
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException, 
    TimeoutException,
    WebDriverException
)
import requests
from bs4 import BeautifulSoup

from core.logging import get_logger
from core.exceptions import AutomationError

# Configure logger
logger = get_logger(__name__)


class BrowserAutomation:
    """Handles browser automation using Selenium."""
    
    def __init__(self, headless: bool = False):
        """
        Initialize browser automation
        
        Args:
            headless (bool): Whether to run the browser in headless mode
        """
        self.driver = None
        self.headless = headless
    
    def start_browser(self) -> webdriver.Chrome:
        """
        Start a Chrome browser instance
        
        Returns:
            webdriver.Chrome: Chrome WebDriver instance
            
        Raises:
            AutomationError: If the browser could not be started
        """
        try:
            # Configure Chrome options
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-popup-blocking")
            chrome_options.add_argument("--disable-notifications")
            
            # Start Chrome driver
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("Chrome browser started")
            return self.driver
            
        except Exception as e:
            logger.error(f"Error starting browser: {str(e)}")
            raise AutomationError(f"Browser start error", details={"error": str(e)})
    
    def navigate_to(self, url: str, wait_time: int = 10) -> bool:
        """
        Navigate to a URL
        
        Args:
            url (str): URL to navigate to
            wait_time (int): Time to wait for page load in seconds
            
        Returns:
            bool: True if navigation was successful
            
        Raises:
            AutomationError: If navigation fails
        """
        try:
            # Start browser if not already started
            if not self.driver:
                self.start_browser()
                
            # Navigate to URL
            logger.info(f"Navigating to: {url}")
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(wait_time)
            return True
            
        except Exception as e:
            logger.error(f"Error navigating to {url}: {str(e)}")
            raise AutomationError(f"Navigation error", details={"url": url, "error": str(e)})
    
    def find_element(self, 
                   selector: str, 
                   by: str = By.CSS_SELECTOR, 
                   wait_time: int = 10,
                   click: bool = False) -> Optional[Any]:
        """
        Find an element on the page
        
        Args:
            selector (str): Element selector
            by (str): Selector type (e.g., By.CSS_SELECTOR, By.XPATH)
            wait_time (int): Time to wait for element in seconds
            click (bool): Whether to click the element after finding it
            
        Returns:
            WebElement or None: Found element or None if not found
            
        Raises:
            AutomationError: If the browser is not started
        """
        if not self.driver:
            raise AutomationError("Browser not started")
            
        try:
            # Wait for element to be present
            element = WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((by, selector))
            )
            
            # Click element if requested
            if click and element:
                element.click()
                
            return element
            
        except (NoSuchElementException, TimeoutException) as e:
            logger.warning(f"Element not found: {selector}")
            return None
        except Exception as e:
            logger.error(f"Error finding element: {str(e)}")
            return None
    
    def find_elements(self, 
                    selector: str, 
                    by: str = By.CSS_SELECTOR, 
                    wait_time: int = 10) -> List[Any]:
        """
        Find multiple elements on the page
        
        Args:
            selector (str): Element selector
            by (str): Selector type (e.g., By.CSS_SELECTOR, By.XPATH)
            wait_time (int): Time to wait for elements in seconds
            
        Returns:
            list: List of found elements
            
        Raises:
            AutomationError: If the browser is not started
        """
        if not self.driver:
            raise AutomationError("Browser not started")
            
        try:
            # Wait for at least one element to be present
            WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((by, selector))
            )
            
            # Get all matching elements
            elements = self.driver.find_elements(by, selector)
            return elements
            
        except (NoSuchElementException, TimeoutException) as e:
            logger.warning(f"Elements not found: {selector}")
            return []
        except Exception as e:
            logger.error(f"Error finding elements: {str(e)}")
            return []
    
    def get_page_content(self) -> str:
        """
        Get the current page's HTML content
        
        Returns:
            str: Page HTML content
            
        Raises:
            AutomationError: If the browser is not started
        """
        if not self.driver:
            raise AutomationError("Browser not started")
            
        return self.driver.page_source
    
    def close_browser(self) -> None:
        """Close the browser."""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                logger.info("Browser closed")
            except Exception as e:
                logger.error(f"Error closing browser: {str(e)}")
    
    def __del__(self):
        """Destructor to ensure browser is closed."""
        self.close_browser()


def fetch_webpage_content(url: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Fetch webpage content using requests and BeautifulSoup (non-browser method)
    
    Args:
        url (str): URL to fetch
        timeout (int): Request timeout in seconds
        
    Returns:
        dict: Webpage content information
        
    Raises:
        AutomationError: If the request fails
    """
    try:
        logger.info(f"Fetching webpage content: {url}")
        
        # Send request with appropriate user agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        
        # Check if request was successful
        if response.status_code != 200:
            raise AutomationError(f"HTTP error: {response.status_code}", 
                                details={"url": url, "status_code": response.status_code})
        
        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract useful information
        title = soup.title.text if soup.title else "No title"
        
        # Get main content (this is a simplistic approach)
        main_content = ""
        for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            main_content += f"{tag.text.strip()}\n\n"
        
        # Return structured content
        return {
            "url": url,
            "title": title,
            "content": main_content,
            "html": response.text
        }
        
    except requests.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        raise AutomationError(f"Request error", details={"url": url, "error": str(e)})
    except Exception as e:
        logger.error(f"Error fetching webpage: {str(e)}")
        raise AutomationError(f"Webpage fetch error", details={"url": url, "error": str(e)}) 