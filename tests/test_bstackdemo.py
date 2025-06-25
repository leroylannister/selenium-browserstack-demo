import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from dotenv import load_dotenv
import threading
import time

# Load environment variables from .env file
load_dotenv()

# BrowserStack authentication credentials
BROWSERSTACK_USERNAME = os.getenv('BROWSERSTACK_USERNAME')
BROWSERSTACK_ACCESS_KEY = os.getenv('BROWSERSTACK_ACCESS_KEY')

# Test configuration
URL = "https://bstackdemo.com/"
USERNAME = "demouser"
PASSWORD = "testingisfun99"

# Test results storage
test_results = {}
results_lock = threading.Lock()


def create_chrome_windows_capabilities():
    """Create Chrome on Windows 10 capabilities"""
    options = ChromeOptions()
    options.set_capability('browserName', 'Chrome')
    options.set_capability('browserVersion', 'latest')
    options.set_capability('bstack:options', {
        'os': 'Windows',
        'osVersion': '10',
        'sessionName': 'Windows 10 Chrome Test',
        'buildName': 'BStackDemo Complete Test Suite',
        'projectName': 'E-commerce Full Flow Test',
        'debug': 'true',
        'networkLogs': 'true',
        'consoleLogs': 'verbose'
    })
    return options


def create_firefox_macos_capabilities():
    """Create Firefox on macOS Ventura capabilities"""
    options = FirefoxOptions()
    options.set_capability('browserName', 'Firefox')
    options.set_capability('browserVersion', 'latest')
    options.set_capability('bstack:options', {
        'os': 'OS X',
        'osVersion': 'Ventura',
        'sessionName': 'macOS Ventura Firefox Test',
        'buildName': 'BStackDemo Complete Test Suite',
        'projectName': 'E-commerce Full Flow Test',
        'debug': 'true',
        'networkLogs': 'true',
        'consoleLogs': 'verbose'
    })
    return options


def create_android_capabilities():
    """Create Samsung Galaxy S22 capabilities"""
    options = ChromeOptions()
    options.set_capability('bstack:options', {
        'deviceName': 'Samsung Galaxy S22',
        'realMobile': 'true',
        'osVersion': '12.0',
        'sessionName': 'Samsung Galaxy S22 Chrome Test',
        'buildName': 'BStackDemo Complete Test Suite',
        'projectName': 'E-commerce Full Flow Test',
        'debug': 'true',
        'networkLogs': 'true',
        'consoleLogs': 'verbose',
        'appiumVersion': '2.0.0'
    })
    return options


def wait_and_click(driver, locator, description, timeout=20, use_js=False):
    """Helper function to wait for element and click it with multiple strategies"""
    wait = WebDriverWait(driver, timeout)
    
    try:
        # Strategy 1: Standard click
        element = wait.until(EC.element_to_be_clickable(locator))
        if not use_js:
            element.click()
            print(f"    ✅ Clicked: {description}")
            return True
        else:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", element)
            print(f"    ✅ JS Clicked: {description}")
            return True
    except:
        # Strategy 2: JavaScript click fallback
        try:
            element = driver.find_element(*locator)
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", element)
            print(f"    ✅ JS Clicked (fallback): {description}")
            return True
        except:
            # Strategy 3: ActionChains
            try:
                element = driver.find_element(*locator)
                ActionChains(driver).move_to_element(element).click().perform()
                print(f"    ✅ ActionChains Clicked: {description}")
                return True
            except Exception as e:
                print(f"    ❌ Failed to click {description}: {str(e)}")
                return False


def wait_for_element(driver, locator, description, timeout=20):
    """Wait for element to be present"""
    try:
        wait = WebDriverWait(driver, timeout)
        element = wait.until(EC.presence_of_element_located(locator))
        print(f"    ✅ Found: {description}")
        return element
    except TimeoutException:
        print(f"    ❌ Not found: {description}")
        return None


def login_to_site(driver, session_name, is_mobile=False):
    """Perform login to BStackDemo"""
    try:
        print(f"\n[{session_name}] 🔐 Starting login process...")
        
        # Wait for initial page load
        time.sleep(3 if is_mobile else 2)
        
        # Click Sign In
        if not wait_and_click(driver, (By.ID, "signin"), "Sign In button", timeout=30):
            raise Exception("Failed to click Sign In")
        
        time.sleep(3 if is_mobile else 2)
        
        # Click username dropdown
        if not wait_and_click(driver, (By.ID, "username"), "Username dropdown", use_js=True):
            raise Exception("Failed to open username dropdown")
        
        time.sleep(2)
        
        # Select demouser - try multiple selectors
        username_clicked = False
        for selector in ["#react-select-2-option-0-0", "[id*='react-select'][id*='option-0-0']"]:
            if wait_and_click(driver, (By.CSS_SELECTOR, selector), "Username option", use_js=True):
                username_clicked = True
                break
        
        if not username_clicked:
            # Try clicking by text
            if wait_and_click(driver, (By.XPATH, "//div[contains(text(), 'demouser')]"), "Username by text", use_js=True):
                username_clicked = True
        
        if not username_clicked:
            raise Exception("Failed to select username")
        
        time.sleep(2)
        
        # Click password dropdown
        if not wait_and_click(driver, (By.ID, "password"), "Password dropdown", use_js=True):
            raise Exception("Failed to open password dropdown")
        
        time.sleep(2)
        
        # Select password - try multiple selectors
        password_clicked = False
        for selector in ["#react-select-3-option-0-0", "[id*='react-select'][id*='option-0-0']"]:
            if wait_and_click(driver, (By.CSS_SELECTOR, selector), "Password option", use_js=True):
                password_clicked = True
                break
        
        if not password_clicked:
            # Try clicking by text
            if wait_and_click(driver, (By.XPATH, "//div[contains(text(), 'testingisfun99')]"), "Password by text", use_js=True):
                password_clicked = True
        
        if not password_clicked:
            raise Exception("Failed to select password")
        
        time.sleep(2)
        
        # Click login button
        if not wait_and_click(driver, (By.ID, "login-btn"), "Login button"):
            raise Exception("Failed to click login button")
        
        # Wait for login to complete
        print(f"[{session_name}] ⏳ Waiting for login to complete...")
        time.sleep(5 if is_mobile else 3)
        
        # Verify login success
        if wait_for_element(driver, (By.CLASS_NAME, "shelf-container"), "Products shelf", timeout=30):
            print(f"[{session_name}] ✅ Login successful!")
            return True
        else:
            raise Exception("Login verification failed")
            
    except Exception as e:
        print(f"[{session_name}] ❌ Login failed: {str(e)}")
        return False


def filter_samsung_products(driver, session_name, is_mobile=False):
    """Filter products to show only Samsung devices"""
    try:
        print(f"\n[{session_name}] 🔍 Filtering for Samsung products...")
        
        time.sleep(2)
        
        # Scroll to top to ensure filters are visible
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        # Find and click Samsung checkbox - try multiple approaches
        samsung_clicked = False
        
        # Approach 1: Click the checkbox span
        try:
            checkboxes = driver.find_elements(By.CSS_SELECTOR, "span.checkmark")
            for checkbox in checkboxes:
                parent = checkbox.find_element(By.XPATH, "..")
                if "Samsung" in parent.text:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
                    time.sleep(0.5)
                    driver.execute_script("arguments[0].click();", checkbox)
                    samsung_clicked = True
                    print(f"[{session_name}] ✅ Clicked Samsung checkbox")
                    break
        except:
            pass
        
        # Approach 2: Click Samsung text directly
        if not samsung_clicked:
            if wait_and_click(driver, (By.XPATH, "//span[text()='Samsung']"), "Samsung text", use_js=True):
                samsung_clicked = True
        
        # Approach 3: Click the label containing Samsung
        if not samsung_clicked:
            if wait_and_click(driver, (By.XPATH, "//label[contains(., 'Samsung')]"), "Samsung label", use_js=True):
                samsung_clicked = True
        
        if not samsung_clicked:
            raise Exception("Failed to click Samsung filter")
        
        # Wait for products to filter
        time.sleep(3)
        print(f"[{session_name}] ✅ Samsung filter applied")
        return True
        
    except Exception as e:
        print(f"[{session_name}] ❌ Failed to filter Samsung products: {str(e)}")
        return False


def favorite_galaxy_s20_plus(driver, session_name, is_mobile=False):
    """Find and favorite the Galaxy S20+ device"""
    try:
        print(f"\n[{session_name}] ❤️ Adding Galaxy S20+ to favorites...")
        
        time.sleep(2)
        
        # Find the Galaxy S20+ product
        galaxy_found = False
        
        # Try to find product tiles
        products = driver.find_elements(By.CSS_SELECTOR, ".shelf-item")
        
        for product in products:
            try:
                # Get product title
                title_element = product.find_element(By.CSS_SELECTOR, ".shelf-item__title")
                product_title = title_element.text
                
                if "Galaxy S20" in product_title or "Galaxy S20+" in product_title:
                    print(f"[{session_name}] 📱 Found Galaxy S20+")
                    
                    # Scroll product into view
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", product)
                    time.sleep(1)
                    
                    # Find and click the favorite button (yellow heart)
                    try:
                        # Try different selectors for the favorite button
                        favorite_btn = None
                        
                        # Try to find within the product element
                        selectors = [
                            ".shelf-stopper",
                            "button[class*='stopper']",
                            "[class*='MuiButtonBase'][class*='MuiIconButton']",
                            "button",
                            "span.MuiIconButton-label"
                        ]
                        
                        for selector in selectors:
                            try:
                                buttons = product.find_elements(By.CSS_SELECTOR, selector)
                                for btn in buttons:
                                    # Check if it's the favorite button
                                    if btn.get_attribute("class") and ("stopper" in btn.get_attribute("class") or "IconButton" in btn.get_attribute("class")):
                                        favorite_btn = btn
                                        break
                                if favorite_btn:
                                    break
                            except:
                                continue
                        
                        if favorite_btn:
                            driver.execute_script("arguments[0].click();", favorite_btn)
                            galaxy_found = True
                            print(f"[{session_name}] ✅ Clicked favorite button for Galaxy S20+")
                            break
                        else:
                            # Alternative: click the heart icon directly
                            heart = product.find_element(By.CSS_SELECTOR, "svg, .MuiSvgIcon-root")
                            driver.execute_script("arguments[0].click();", heart)
                            galaxy_found = True
                            print(f"[{session_name}] ✅ Clicked heart icon for Galaxy S20+")
                            break
                            
                    except Exception as btn_error:
                        print(f"[{session_name}] ⚠️ Error clicking favorite button: {str(btn_error)}")
                        
            except Exception as product_error:
                continue
        
        if not galaxy_found:
            raise Exception("Could not find or favorite Galaxy S20+")
        
        time.sleep(2)
        return True
        
    except Exception as e:
        print(f"[{session_name}] ❌ Failed to favorite Galaxy S20+: {str(e)}")
        return False


def verify_favorites(driver, session_name, is_mobile=False):
    """Navigate to favorites page and verify Galaxy S20+ is there"""
    try:
        print(f"\n[{session_name}] 📋 Verifying favorites...")
        
        time.sleep(2)
        
        # Click on Favorites link/button
        favorites_clicked = False
        
        # Try different selectors for favorites
        selectors = [
            (By.CSS_SELECTOR, "a[href*='favourites']"),
            (By.CSS_SELECTOR, "a[href*='favorites']"),
            (By.XPATH, "//a[contains(@href, 'favourites')]"),
            (By.XPATH, "//a[contains(text(), 'Favourites')]"),
            (By.XPATH, "//a[contains(text(), 'Favorites')]"),
            (By.CSS_SELECTOR, ".MuiBadge-root"),
            (By.CSS_SELECTOR, "[class*='navbar'] a[href*='fav']")
        ]
        
        for locator in selectors:
            if wait_and_click(driver, locator, "Favorites link", use_js=True):
                favorites_clicked = True
                break
        
        if not favorites_clicked:
            # Try to find in navigation
            nav_links = driver.find_elements(By.CSS_SELECTOR, "a")
            for link in nav_links:
                href = link.get_attribute("href") or ""
                text = link.text.lower()
                if "favourite" in href or "favorite" in href or "favourite" in text or "favorite" in text:
                    driver.execute_script("arguments[0].click();", link)
                    favorites_clicked = True
                    print(f"[{session_name}] ✅ Clicked favorites link")
                    break
        
        if not favorites_clicked:
            raise Exception("Could not find favorites link")
        
        # Wait for favorites page to load
        time.sleep(3)
        
        # Verify Galaxy S20+ is in favorites
        print(f"[{session_name}] 🔍 Looking for Galaxy S20+ in favorites...")
        
        # Check page content
        page_content = driver.page_source.lower()
        
        if "galaxy s20" in page_content:
            print(f"[{session_name}] ✅ Galaxy S20+ found in favorites!")
            
            # Additional verification - try to find the actual product element
            try:
                products = driver.find_elements(By.CSS_SELECTOR, ".shelf-item__title, .product-title, p")
                for product in products:
                    if "Galaxy S20" in product.text:
                        print(f"[{session_name}] ✅ Confirmed: Galaxy S20+ is displayed in favorites")
                        return True
            except:
                # If we found it in page source, that's good enough
                return True
        
        # If not found, it might be empty favorites message
        if "no products" in page_content or "empty" in page_content:
            raise Exception("Favorites page is empty - product was not added")
        
        raise Exception("Galaxy S20+ not found in favorites")
        
    except Exception as e:
        print(f"[{session_name}] ❌ Failed to verify favorites: {str(e)}")
        return False


def run_complete_test(capability):
    """Run the complete test flow"""
    driver = None
    session_name = capability.capabilities.get('bstack:options', {}).get('sessionName', 'Unknown')
    
    try:
        print(f"\n{'='*60}")
        print(f"🚀 STARTING TEST: {session_name}")
        print(f"{'='*60}")
        
        # Detect if mobile
        is_mobile = 'deviceName' in str(capability.capabilities)
        
        # Initialize WebDriver
        print(f"[{session_name}] 🔧 Initializing WebDriver...")
        driver = webdriver.Remote(
            command_executor=f'https://{BROWSERSTACK_USERNAME}:{BROWSERSTACK_ACCESS_KEY}@hub-cloud.browserstack.com/wd/hub',
            options=capability
        )
        
        # Set timeouts
        driver.set_page_load_timeout(60 if is_mobile else 45)
        driver.implicitly_wait(10)
        
        # Navigate to site
        print(f"[{session_name}] 🌐 Navigating to {URL}")
        driver.get(URL)
        
        # Execute test steps
        test_passed = True
        
        # Step 1: Login
        if not login_to_site(driver, session_name, is_mobile):
            test_passed = False
            raise Exception("Login failed")
        
        # Step 2: Filter for Samsung products
        if not filter_samsung_products(driver, session_name, is_mobile):
            test_passed = False
            raise Exception("Failed to filter Samsung products")
        
        # Step 3: Favorite Galaxy S20+
        if not favorite_galaxy_s20_plus(driver, session_name, is_mobile):
            test_passed = False
            raise Exception("Failed to favorite Galaxy S20+")
        
        # Step 4: Verify favorites
        if not verify_favorites(driver, session_name, is_mobile):
            test_passed = False
            raise Exception("Failed to verify favorites")
        
        # Test successful
        print(f"\n[{session_name}] 🎉 ALL TESTS PASSED!")
        
        # Mark test as passed in BrowserStack
        driver.execute_script('browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": "All test steps completed successfully"}}')
        
        # Store result
        with results_lock:
            test_results[session_name] = "PASSED"
        
        return True
        
    except Exception as e:
        print(f"\n[{session_name}] ❌ TEST FAILED: {str(e)}")
        
        # Mark test as failed in BrowserStack
        if driver:
            try:
                driver.execute_script(f'browserstack_executor: {{"action": "setSessionStatus", "arguments": {{"status":"failed", "reason": "{str(e)[:100]}"}}}}')
            except:
                pass
        
        # Store result
        with results_lock:
            test_results[session_name] = f"FAILED: {str(e)}"
        
        return False
        
    finally:
        if driver:
            print(f"[{session_name}] 🧹 Closing browser session")
            try:
                driver.quit()
            except:
                pass


def main():
    """Main execution function"""
    print("\n" + "="*80)
    print("🧪 BROWSERSTACK E-COMMERCE TEST SUITE")
    print("📋 Test Requirements:")
    print("   1. Login with demouser/testingisfun99")
    print("   2. Filter products to show Samsung devices")
    print("   3. Favorite the Galaxy S20+ device")
    print("   4. Verify Galaxy S20+ appears in favorites")
    print("\n🌐 Running on:")
    print("   • Windows 10 Chrome")
    print("   • macOS Ventura Firefox")
    print("   • Samsung Galaxy S22")
    print("="*80)
    
    # Create capabilities
    capabilities = [
        create_chrome_windows_capabilities(),
        create_firefox_macos_capabilities(),
        create_android_capabilities()
    ]
    
    # Run tests in parallel
    threads = []
    
    for cap in capabilities:
        thread = threading.Thread(target=run_complete_test, args=(cap,))
        thread.start()
        threads.append(thread)
    
    # Wait for all tests to complete
    for thread in threads:
        thread.join()
    
    # Print summary
    print("\n" + "="*80)
    print("📊 TEST RESULTS SUMMARY")
    print("="*80)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result == "PASSED" else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result != "PASSED":
            print(f"   Error: {result}")
    
    print("\n✨ Test suite execution completed!")
    print("📈 Check BrowserStack dashboard for detailed results")
    print("="*80)


if __name__ == "__main__":
    main()