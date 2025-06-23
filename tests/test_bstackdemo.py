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
chrome_options.set_capability('bstack:options', {
    'os': 'Windows',
    'osVersion': '10',
    'sessionName': 'Windows Chrome Test'  # Displayed in BrowserStack dashboard
})

# Browser configuration for macOS Firefox desktop testing
firefox_options = FirefoxOptions()
firefox_options.set_capability('browserName', 'Firefox')
firefox_options.set_capability('bstack:options', {
    'os': 'OS X',
    'osVersion': 'Ventura',
    'sessionName': 'macOS Firefox Test'  # Displayed in BrowserStack dashboard
})

# Mobile device configuration for Android testing
# Note: Using ChromeOptions for mobile Chrome browser on Android
android_options = ChromeOptions()
android_options.set_capability('deviceName', 'Samsung Galaxy S22')
android_options.set_capability('realMobile', 'true')  # Use real device, not emulator
android_options.set_capability('osVersion', '12.0')
android_options.set_capability('browserName', 'Android')
android_options.set_capability('bstack:options', {
    'sessionName': 'Galaxy S22 Test'  # Displayed in BrowserStack dashboard
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
    # Initialize remote WebDriver connection to BrowserStack
    driver = webdriver.Remote(
        command_executor=f'https://{BROWSERSTACK_USERNAME}:{BROWSERSTACK_ACCESS_KEY}@hub-cloud.browserstack.com/wd/hub',
        options=cap
    )
    
    try:
        # Set up explicit wait with 20-second timeout for all element interactions
        wait = WebDriverWait(driver, 20)
        
        # Navigate to the demo e-commerce site
        driver.get(URL)

        # Step 1: Initiate login process
        wait.until(EC.element_to_be_clickable((By.ID, "signin"))).click()
        
        # Step 2: Select username from dropdown
        # Click username field to open dropdown
        wait.until(EC.element_to_be_clickable((By.ID, "username"))).click()
        # Select first option from username dropdown (demouser)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#react-select-2-option-0-0"))).click()
        
        # Step 3: Select password from dropdown
        # Click password field to open dropdown
        wait.until(EC.element_to_be_clickable((By.ID, "password"))).click()
        # Select first option from password dropdown (testingisfun99)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#react-select-3-option-0-0"))).click()
        
        # Step 4: Complete login
        wait.until(EC.element_to_be_clickable((By.ID, "login-btn"))).click()
        
        # Step 5: Apply Samsung brand filter
        # Click on the brand filter section (second filter div)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.filters > div:nth-child(2)"))).click()
        # Check the Samsung checkbox by finding the input preceding the Samsung label
        wait.until(EC.element_to_be_clickable((By.XPATH, "//label[text()='Samsung']/preceding-sibling::input"))).click()
        
        # Step 6: Add Galaxy S20+ to favorites
        # Find the Galaxy S20+ product and click its wishlist/heart icon
        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Galaxy S20+']/ancestor::div[contains(@class,'shelf-item')]//span[contains(@class,'wishlistIcon')]"))).click()
        
        # Step 7: Navigate to favorites page
        wait.until(EC.element_to_be_clickable((By.ID, "wishlist"))).click()
        
        # Step 8: Verify test success
        # Check that Galaxy S20+ appears in the favorites page content
        assert "Galaxy S20+" in driver.page_source, "Galaxy S20+ not found in favorites"
        print(f"Test passed successfully on {cap.capabilities.get('sessionName', 'Unknown browser')}!")
        
    except Exception as e:
        # Log any test failures with browser information
        session_name = cap.capabilities.get('sessionName', 'Unknown browser')
        print(f"Test failed on {session_name}: {str(e)}")
    finally:
        # Always close the browser session to free up resources
        driver.quit()

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
print("All tests completed!")