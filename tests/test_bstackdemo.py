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

# Load environment variables
load_dotenv()

BROWSERSTACK_USERNAME = os.getenv('BROWSERSTACK_USERNAME')
BROWSERSTACK_ACCESS_KEY = os.getenv('BROWSERSTACK_ACCESS_KEY')

URL = "https://bstackdemo.com/"
USERNAME = "demouser"
PASSWORD = "testingisfun99"

# For Windows Chrome
chrome_options = ChromeOptions()
chrome_options.set_capability('browserName', 'Chrome')
chrome_options.set_capability('bstack:options', {
    'os': 'Windows',
    'osVersion': '10',
    'sessionName': 'Windows Chrome Test'
})

# For macOS Firefox
firefox_options = FirefoxOptions()
firefox_options.set_capability('browserName', 'Firefox')
firefox_options.set_capability('bstack:options', {
    'os': 'OS X',
    'osVersion': 'Ventura',
    'sessionName': 'macOS Firefox Test'
})

# For Samsung Galaxy S22 (using ChromeOptions for mobile)
android_options = ChromeOptions()
android_options.set_capability('deviceName', 'Samsung Galaxy S22')
android_options.set_capability('realMobile', 'true')
android_options.set_capability('osVersion', '12.0')
android_options.set_capability('browserName', 'Android')
android_options.set_capability('bstack:options', {
    'sessionName': 'Galaxy S22 Test'
})

# Create the capabilities list
capabilities = [chrome_options, firefox_options, android_options]

def run_test(cap):
    driver = webdriver.Remote(
        command_executor=f'https://{BROWSERSTACK_USERNAME}:{BROWSERSTACK_ACCESS_KEY}@hub-cloud.browserstack.com/wd/hub',
        options=cap
    )
    
    try:
        wait = WebDriverWait(driver, 20)
        driver.get(URL)

        # Click Sign In
        wait.until(EC.element_to_be_clickable((By.ID, "signin"))).click()
        
        # Select username
        wait.until(EC.element_to_be_clickable((By.ID, "username"))).click()
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#react-select-2-option-0-0"))).click()
        
        # Select password
        wait.until(EC.element_to_be_clickable((By.ID, "password"))).click()
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#react-select-3-option-0-0"))).click()
        
        # Click Login
        wait.until(EC.element_to_be_clickable((By.ID, "login-btn"))).click()
        
        # Filter for Samsung
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.filters > div:nth-child(2)"))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, "//label[text()='Samsung']/preceding-sibling::input"))).click()
        
        # Favorite Galaxy S20+
        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Galaxy S20+']/ancestor::div[contains(@class,'shelf-item')]//span[contains(@class,'wishlistIcon')]"))).click()
        
        # Go to Favorites page
        wait.until(EC.element_to_be_clickable((By.ID, "wishlist"))).click()
        
        # Verify Galaxy S20+ is listed
        assert "Galaxy S20+" in driver.page_source, "Galaxy S20+ not found in favorites"
        print("Test passed successfully!")
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
    finally:
        driver.quit()

# Run tests in parallel
threads = []
for cap in capabilities:
    t = threading.Thread(target=run_test, args=(cap,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print("All tests completed!")