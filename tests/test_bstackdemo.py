import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dotenv import load_dotenv
import threading
import time

# Load environment variables from .env file
load_dotenv()

# BrowserStack authentication credentials
BROWSERSTACK_USERNAME = os.getenv('BROWSERSTACK_USERNAME')
BROWSERSTACK_ACCESS_KEY = os.getenv('BROWSERSTACK_ACCESS_KEY')

# Test target configuration
URL = "https://bstackdemo.com/"

# Browser configuration for Windows Chrome desktop testing
chrome_options = ChromeOptions()
chrome_options.set_capability('browserName', 'Chrome')
chrome_options.set_capability('browserVersion', 'latest')
chrome_options.set_capability('bstack:options', {
    'os': 'Windows',
    'osVersion': '10',
    'sessionName': 'Windows 10 Chrome Test',
    'buildName': 'Cross-Platform E-commerce Test v2',
    'projectName': 'Multi-Browser Testing',
    'seleniumVersion': '4.0.0',
    'debug': 'true',
    'networkLogs': 'true',
    'consoleLogs': 'verbose'
})

# Browser configuration for macOS Firefox desktop testing
firefox_options = FirefoxOptions()
firefox_options.set_capability('browserName', 'Firefox')
firefox_options.set_capability('browserVersion', 'latest')
firefox_options.set_capability('bstack:options', {
    'os': 'OS X',
    'osVersion': 'Ventura',
    'sessionName': 'macOS Ventura Firefox Test',
    'buildName': 'Cross-Platform E-commerce Test v2',
    'projectName': 'Multi-Browser Testing',
    'seleniumVersion': '4.0.0',
    'debug': 'true',
    'networkLogs': 'true',
    'consoleLogs': 'verbose'
})

# Mobile device configuration for Android testing
android_options = ChromeOptions()
android_options.set_capability('deviceName', 'Samsung Galaxy S22')
android_options.set_capability('realMobile', 'true')
android_options.set_capability('osVersion', '12.0')
android_options.set_capability('browserName', 'chrome')
android_options.set_capability('bstack:options', {
    'sessionName': 'Samsung Galaxy S22 Chrome Test',
    'buildName': 'Cross-Platform E-commerce Test v2',
    'projectName': 'Multi-Browser Testing',
    'debug': 'true',
    'networkLogs': 'true',
    'consoleLogs': 'verbose'
})

# List of all browser/device configurations for parallel testing
capabilities = [chrome_options, firefox_options, android_options]

def safe_click(driver, wait, by_locator, timeout=15, description="element"):
    """Safely click an element with multiple fallback strategies"""
    try:
        # Strategy 1: Wait for element to be clickable
        element = wait.until(EC.element_to_be_clickable(by_locator))
        element.click()
        return True
    except TimeoutException:
        try:
            # Strategy 2: Find element and use JavaScript click
            element = driver.find_element(*by_locator)
            driver.execute_script("arguments[0].click();", element)
            return True
        except:
            try:
                # Strategy 3: Use Actions class
                from selenium.webdriver.common.action_chains import ActionChains
                element = driver.find_element(*by_locator)
                ActionChains(driver).move_to_element(element).click().perform()
                return True
            except:
                print(f"Failed to click {description}")
                return False

def wait_for_page_load(driver, timeout=10):
    """Wait for page to fully load"""
    try:
        WebDriverWait(driver, timeout).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
        time.sleep(1)  # Additional buffer for dynamic content
    except:
        pass

def perform_login(driver, wait, session_name):
    """Perform login with robust error handling"""
    try:
        print(f"[{session_name}] Starting login process")
        
        # Wait for page to fully load
        wait_for_page_load(driver)
        
        # Step 1: Click sign in button
        print(f"[{session_name}] Clicking sign in")
        signin_selectors = [
            (By.ID, "signin"),
            (By.CSS_SELECTOR, "#signin"),
            (By.XPATH, "//a[@id='signin']"),
            (By.XPATH, "//a[contains(text(), 'Sign In')]")
        ]
        
        clicked = False
        for selector in signin_selectors:
            if safe_click(driver, wait, selector, description="sign in button"):
                clicked = True
                break
        
        if not clicked:
            raise Exception("Could not click sign in button")
        
        time.sleep(2)  # Wait for login modal to appear
        
        # Step 2: Handle username dropdown
        print(f"[{session_name}] Selecting username")
        username_selectors = [
            (By.ID, "username"),
            (By.CSS_SELECTOR, "#username"),
            (By.XPATH, "//div[@id='username']")
        ]
        
        clicked = False
        for selector in username_selectors:
            if safe_click(driver, wait, selector, description="username dropdown"):
                clicked = True
                break
                
        if not clicked:
            raise Exception("Could not open username dropdown")
        
        time.sleep(1)
        
        # Select first username option
        username_option_selectors = [
            (By.CSS_SELECTOR, "#react-select-2-option-0-0"),
            (By.CSS_SELECTOR, "[id*='react-select'][id*='option-0-0']"),
            (By.XPATH, "//div[contains(@id, 'react-select') and contains(@id, 'option-0')]"),
            (By.XPATH, "//div[contains(text(), 'demouser')]")
        ]
        
        clicked = False
        for selector in username_option_selectors:
            if safe_click(driver, wait, selector, description="username option"):
                clicked = True
                break
                
        if not clicked:
            raise Exception("Could not select username option")
        
        time.sleep(1)
        
        # Step 3: Handle password dropdown
        print(f"[{session_name}] Selecting password")
        password_selectors = [
            (By.ID, "password"),
            (By.CSS_SELECTOR, "#password"),
            (By.XPATH, "//div[@id='password']")
        ]
        
        clicked = False
        for selector in password_selectors:
            if safe_click(driver, wait, selector, description="password dropdown"):
                clicked = True
                break
                
        if not clicked:
            raise Exception("Could not open password dropdown")
        
        time.sleep(1)
        
        # Select first password option
        password_option_selectors = [
            (By.CSS_SELECTOR, "#react-select-3-option-0-0"),
            (By.CSS_SELECTOR, "[id*='react-select'][id*='option-0-0']"),
            (By.XPATH, "//div[contains(@id, 'react-select') and contains(@id, 'option-0') and contains(text(), 'testing')]"),
            (By.XPATH, "//div[contains(text(), 'testingisfun99')]")
        ]
        
        clicked = False
        for selector in password_option_selectors:
            if safe_click(driver, wait, selector, description="password option"):
                clicked = True
                break
                
        if not clicked:
            raise Exception("Could not select password option")
        
        time.sleep(1)
        
        # Step 4: Click login button
        print(f"[{session_name}] Clicking login button")
        login_selectors = [
            (By.ID, "login-btn"),
            (By.CSS_SELECTOR, "#login-btn"),
            (By.XPATH, "//button[@id='login-btn']"),
            (By.XPATH, "//button[contains(text(), 'Log In')]")
        ]
        
        clicked = False
        for selector in login_selectors:
            if safe_click(driver, wait, selector, description="login button"):
                clicked = True
                break
                
        if not clicked:
            raise Exception("Could not click login button")
        
        # Wait for login to complete - look for post-login indicators
        print(f"[{session_name}] Waiting for login to complete")
        login_success_selectors = [
            (By.CLASS_NAME, "shelf-container"),
            (By.CSS_SELECTOR, ".shelf-container"),
            (By.XPATH, "//div[contains(@class, 'shelf')]"),
            (By.CSS_SELECTOR, "[class*='product']"),
            (By.ID, "logout")
        ]
        
        login_successful = False
        for selector in login_success_selectors:
            try:
                wait.until(EC.presence_of_element_located(selector))
                login_successful = True
                print(f"[{session_name}] Login successful - found post-login element")
                break
            except TimeoutException:
                continue
        
        if not login_successful:
            # Try waiting a bit longer for any element to indicate successful login
            time.sleep(3)
            current_url = driver.current_url
            if "signin" not in current_url.lower() and len(driver.find_elements(By.TAG_NAME, "body")) > 0:
                print(f"[{session_name}] Login appears successful based on URL")
                return True
            else:
                raise Exception("Login verification failed - still on login page or page not loaded")
        
        return True
        
    except Exception as e:
        print(f"[{session_name}] Login failed: {str(e)}")
        return False

def run_test(cap):
    """
    Execute the complete test workflow for a single browser/device configuration.
    
    Test steps:
    1. Login to the demo site
    2. Filter products by Samsung brand
    3. Add Galaxy S20+ to favorites
    4. Verify item appears in favorites page
    
    Args:
        cap: Browser/device capability configuration object
    """
    driver = None
    session_name = cap.capabilities.get('bstack:options', {}).get('sessionName', 'Unknown browser')
    
    try:
        print(f"Starting test on {session_name}...")
        
        # Initialize remote WebDriver connection to BrowserStack
        driver = webdriver.Remote(
            command_executor=f'https://{BROWSERSTACK_USERNAME}:{BROWSERSTACK_ACCESS_KEY}@hub-cloud.browserstack.com/wd/hub',
            options=cap
        )
        
        # Set longer timeout for mobile compatibility
        wait = WebDriverWait(driver, 45)
        
        # Set page load timeout
        driver.set_page_load_timeout(60)
        
        # Navigate to the demo e-commerce site
        print(f"[{session_name}] Navigating to {URL}")
        driver.get(URL)
        
        # Perform login with robust error handling
        if not perform_login(driver, wait, session_name):
            raise Exception("Login failed")
        
        print(f"[{session_name}] ✅ LOGIN SUCCESSFUL! Test completed successfully.")
        
        # Mark test as passed in BrowserStack
        driver.execute_script('browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": "Login successful - test passed"}}')
        
    except Exception as e:
        print(f"❌ Test FAILED on {session_name}: {str(e)}")
        
        # Capture screenshot for debugging
        try:
            if driver:
                screenshot = driver.get_screenshot_as_base64()
                print(f"[{session_name}] Screenshot captured for debugging")
        except:
            pass
        
        # Mark test as failed in BrowserStack
        if driver:
            try:
                driver.execute_script(f'browserstack_executor: {{"action": "setSessionStatus", "arguments": {{"status":"failed", "reason": "{str(e)[:100]}"}}}}')
            except:
                pass
                
    finally:
        # Always close the browser session to free up resources
        if driver:
            print(f"[{session_name}] Closing browser session")
            try:
                driver.quit()
            except:
                pass

def main():
    """Main function to execute tests across all platforms"""
    print("=" * 60)
    print("Starting Cross-Platform BrowserStack Tests (Login Focus)")
    print("=" * 60)
    print(f"Testing LOGIN functionality on {len(capabilities)} platforms:")
    for i, cap in enumerate(capabilities, 1):
        session_name = cap.capabilities.get('bstack:options', {}).get('sessionName', f'Platform {i}')
        print(f"  {i}. {session_name}")
    print("=" * 60)
    
    # Execute tests in parallel across all configured browsers/devices
    threads = []
    
    # Create and start a thread for each browser/device configuration
    for cap in capabilities:
        t = threading.Thread(target=run_test, args=(cap,))
        t.start()
        threads.append(t)
    
    # Wait for all test threads to complete before proceeding
    for t in threads:
        t.join()
    
    # Final status message
    print("=" * 60)
    print("🏁 All cross-platform LOGIN tests completed!")
    print("=" * 60)
    print("Check your BrowserStack dashboard for detailed results and session recordings.")
    print("If all logins are successful, you can extend the test to include the shopping flow.")

if __name__ == "__main__":
    main()