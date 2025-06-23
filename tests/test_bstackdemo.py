import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from dotenv import load_dotenv
import threading
import time

# Load environment variables from .env file
load_dotenv()

# BrowserStack authentication credentials
BROWSERSTACK_USERNAME = os.getenv('BROWSERSTACK_USERNAME')
BROWSERSTACK_ACCESS_KEY = os.getenv('BROWSERSTACK_ACCESS_KEY')

# Test target configuration
URL = "https://bstackdemo.com/"  # Demo e-commerce site for testing
USERNAME = "demouser"            # Demo site login credentials
PASSWORD = "testingisfun99"      # Demo site login credentials

# Browser configuration for Windows Chrome desktop testing
chrome_options = ChromeOptions()
chrome_options.set_capability('browserName', 'Chrome')
chrome_options.set_capability('browserVersion', 'latest')  # Added browser version
chrome_options.set_capability('bstack:options', {
    'os': 'Windows',
    'osVersion': '10',
    'sessionName': 'Windows 10 Chrome Test',  # More descriptive name
    'buildName': 'Cross-Platform E-commerce Test',  # Group tests together
    'projectName': 'Multi-Browser Testing'
})

# Browser configuration for macOS Firefox desktop testing
firefox_options = FirefoxOptions()
firefox_options.set_capability('browserName', 'Firefox')
firefox_options.set_capability('browserVersion', 'latest')  # Added browser version
firefox_options.set_capability('bstack:options', {
    'os': 'OS X',
    'osVersion': 'Ventura',
    'sessionName': 'macOS Ventura Firefox Test',  # More descriptive name
    'buildName': 'Cross-Platform E-commerce Test',
    'projectName': 'Multi-Browser Testing'
})

# Mobile device configuration for Android testing
android_options = ChromeOptions()
android_options.set_capability('deviceName', 'Samsung Galaxy S22')
android_options.set_capability('realMobile', 'true')  # Use real device, not emulator
android_options.set_capability('osVersion', '12.0')
android_options.set_capability('browserName', 'chrome')  # Changed from 'Android' to 'chrome'
android_options.set_capability('bstack:options', {
    'sessionName': 'Samsung Galaxy S22 Chrome Test',  # More descriptive name
    'buildName': 'Cross-Platform E-commerce Test',
    'projectName': 'Multi-Browser Testing'
})

# List of all browser/device configurations for parallel testing
capabilities = [chrome_options, firefox_options, android_options]

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
        
        # Set up explicit wait with 30-second timeout for mobile compatibility
        wait = WebDriverWait(driver, 30)
        
        # Navigate to the demo e-commerce site
        print(f"[{session_name}] Navigating to {URL}")
        driver.get(URL)
        
        # Add a small delay to ensure page loads completely
        time.sleep(2)

        # Step 1: Initiate login process
        print(f"[{session_name}] Clicking sign in button")
        signin_btn = wait.until(EC.element_to_be_clickable((By.ID, "signin")))
        signin_btn.click()
        
        # Step 2: Select username from dropdown
        print(f"[{session_name}] Selecting username")
        username_field = wait.until(EC.element_to_be_clickable((By.ID, "username")))
        username_field.click()
        
        # Wait for dropdown to appear and select first option
        username_option = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#react-select-2-option-0-0")))
        username_option.click()
        
        # Step 3: Select password from dropdown
        print(f"[{session_name}] Selecting password")
        password_field = wait.until(EC.element_to_be_clickable((By.ID, "password")))
        password_field.click()
        
        # Wait for dropdown to appear and select first option
        password_option = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#react-select-3-option-0-0")))
        password_option.click()
        
        # Step 4: Complete login
        print(f"[{session_name}] Logging in")
        login_btn = wait.until(EC.element_to_be_clickable((By.ID, "login-btn")))
        login_btn.click()
        
        # Wait for login to complete by checking for a post-login element
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "shelf-container")))
        
        # Step 5: Apply Samsung brand filter
        print(f"[{session_name}] Applying Samsung filter")
        # Try multiple selectors for better compatibility across devices
        try:
            brand_filter = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.filters > div:nth-child(2)")))
            brand_filter.click()
        except:
            # Alternative selector if the first one fails
            brand_filter = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='filters']//div[contains(text(),'Brand') or contains(.,'Brand')]")))
            brand_filter.click()
        
        # Check the Samsung checkbox
        samsung_checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[text()='Samsung']/preceding-sibling::input")))
        samsung_checkbox.click()
        
        # Wait for filter to be applied
        time.sleep(2)
        
        # Step 6: Add Galaxy S20+ to favorites
        print(f"[{session_name}] Adding Galaxy S20+ to favorites")
        wishlist_icon = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Galaxy S20+']/ancestor::div[contains(@class,'shelf-item')]//span[contains(@class,'wishlistIcon')]")))
        wishlist_icon.click()
        
        # Wait for the item to be added to wishlist
        time.sleep(1)
        
        # Step 7: Navigate to favorites page
        print(f"[{session_name}] Navigating to favorites page")
        wishlist_btn = wait.until(EC.element_to_be_clickable((By.ID, "wishlist")))
        wishlist_btn.click()
        
        # Step 8: Verify test success
        print(f"[{session_name}] Verifying Galaxy S20+ in favorites")
        # Wait for favorites page to load
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "shelf-container")))
        
        # Check that Galaxy S20+ appears in the favorites page content
        assert "Galaxy S20+" in driver.page_source, "Galaxy S20+ not found in favorites"
        print(f"✅ Test PASSED successfully on {session_name}!")
        
        # Mark test as passed in BrowserStack
        driver.execute_script('browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": "Test completed successfully"}}')
        
    except Exception as e:
        # Log any test failures with browser information
        print(f"❌ Test FAILED on {session_name}: {str(e)}")
        
        # Mark test as failed in BrowserStack
        if driver:
            try:
                driver.execute_script(f'browserstack_executor: {{"action": "setSessionStatus", "arguments": {{"status":"failed", "reason": "{str(e)}"}}}}')
            except:
                pass  # Ignore if this fails
                
    finally:
        # Always close the browser session to free up resources
        if driver:
            print(f"[{session_name}] Closing browser session")
            driver.quit()

def main():
    """Main function to execute tests across all platforms"""
    print("=" * 60)
    print("Starting Cross-Platform BrowserStack Tests")
    print("=" * 60)
    print(f"Testing on {len(capabilities)} platforms:")
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
    print("🏁 All cross-platform tests completed!")
    print("=" * 60)
    print("Check your BrowserStack dashboard for detailed results and session recordings.")

if __name__ == "__main__":
    main()