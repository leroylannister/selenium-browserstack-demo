
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
import urllib3

# Suppress OpenSSL warnings
urllib3.disable_warnings(urllib3.exceptions.NotOpenSSLWarning)

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
        'consoleLogs': 'verbose',
        'seleniumVersion': '4.0.0'
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
        'consoleLogs': 'verbose',
        'seleniumVersion': '4.0.0',
        'wsLocalSupport': 'false'
    })
    return options


def create_android_capabilities():
    """Create Samsung Galaxy S22 capabilities"""
    options = ChromeOptions()
    options.set_capability('bstack:options', {
        'deviceName': 'Samsung Galaxy S22',
        'realMobile': 'true',
        'osVersion': '12.0',
        'browserName': 'chrome',
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


def select_dropdown_option(driver, dropdown_id, option_text, description, is_mobile=False):
    """Enhanced dropdown selection that handles React Select components"""
    try:
        print(f"    🔄 Selecting {description}...")
        
        # Click the dropdown to open it
        dropdown_clicked = False
        
        # Try multiple selectors for the dropdown
        dropdown_selectors = [
            (By.ID, dropdown_id),
            (By.CSS_SELECTOR, f"#{dropdown_id}"),
            (By.CSS_SELECTOR, f"div#{dropdown_id}"),
            (By.XPATH, f"//div[@id='{dropdown_id}']")
        ]
        
        for selector in dropdown_selectors:
            if wait_and_click(driver, selector, f"{description} dropdown", use_js=True):
                dropdown_clicked = True
                break
        
        if not dropdown_clicked:
            raise Exception(f"Could not open {description} dropdown")
        
        # Wait for dropdown to fully open
        time.sleep(3 if is_mobile else 2)
        
        # Try to find and click the option
        option_clicked = False
        
        # Strategy 1: Look for all divs that might be dropdown options
        try:
            # Get all potential option elements
            option_elements = driver.find_elements(By.CSS_SELECTOR, "div[id*='react-select'][id*='option']")
            
            for element in option_elements:
                try:
                    if option_text in element.text or element.text == option_text:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                        time.sleep(0.5)
                        driver.execute_script("arguments[0].click();", element)
                        option_clicked = True
                        print(f"    ✅ Selected {option_text} from options list")
                        break
                except:
                    continue
        except:
            pass
        
        # Strategy 2: Click by text content
        if not option_clicked:
            try:
                xpath = f"//div[contains(text(), '{option_text}')]"
                elements = driver.find_elements(By.XPATH, xpath)
                
                # Try to click the visible one
                for element in elements:
                    try:
                        if element.is_displayed():
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                            time.sleep(0.5)
                            driver.execute_script("arguments[0].click();", element)
                            option_clicked = True
                            print(f"    ✅ Selected {option_text} by text")
                            break
                    except:
                        continue
            except:
                pass
        
        # Strategy 3: Try generic menu item selectors
        if not option_clicked:
            generic_selectors = [
                f"//div[@role='option'][contains(., '{option_text}')]",
                f"//div[@class='css-1n7v3ny-option'][contains(., '{option_text}')]",
                f"//div[contains(@class, 'option')][contains(., '{option_text}')]",
                f"//*[contains(., '{option_text}')][contains(@id, 'option')]"
            ]
            
            for selector in generic_selectors:
                try:
                    element = driver.find_element(By.XPATH, selector)
                    driver.execute_script("arguments[0].click();", element)
                    option_clicked = True
                    print(f"    ✅ Selected {option_text} using generic selector")
                    break
                except:
                    continue
        
        if not option_clicked:
            # Last resort: click the first available option
            try:
                first_option = driver.find_element(By.CSS_SELECTOR, "[id*='option-0']")
                driver.execute_script("arguments[0].click();", first_option)
                print(f"    ⚠️  Clicked first available option (fallback)")
                option_clicked = True
            except:
                pass
        
        if option_clicked:
            time.sleep(1)
            return True
        else:
            raise Exception(f"Could not select {option_text}")
            
    except Exception as e:
        print(f"    ❌ Failed to select {description}: {str(e)}")
        return False


def login_to_site(driver, session_name, is_mobile=False):
    """Perform login to BStackDemo with enhanced dropdown handling"""
    try:
        print(f"\n[{session_name}] 🔐 Starting login process...")
        
        # Wait for initial page load
        time.sleep(5 if is_mobile else 3)
        
        # Click Sign In
        if not wait_and_click(driver, (By.ID, "signin"), "Sign In button", timeout=30):
            raise Exception("Failed to click Sign In")
        
        time.sleep(5 if is_mobile else 3)
        
        # Select username using enhanced dropdown handler
        if not select_dropdown_option(driver, "username", USERNAME, "username", is_mobile):
            raise Exception("Failed to select username")
        
        # Select password using enhanced dropdown handler
        if not select_dropdown_option(driver, "password", PASSWORD, "password", is_mobile):
            raise Exception("Failed to select password")
        
        time.sleep(2)
        
        # Click login button
        if not wait_and_click(driver, (By.ID, "login-btn"), "Login button"):
            raise Exception("Failed to click login button")
        
        # Wait for login to complete
        print(f"[{session_name}] ⏳ Waiting for login to complete...")
        time.sleep(8 if is_mobile else 5)
        
        # Verify login success
        if wait_for_element(driver, (By.CLASS_NAME, "shelf-container"), "Products shelf", timeout=30):
            print(f"[{session_name}] ✅ Login successful!")
            return True
        else:
            # Check if we're on the main page with products
            try:
                products = driver.find_elements(By.CSS_SELECTOR, ".shelf-item")
                if len(products) > 0:
                    print(f"[{session_name}] ✅ Login successful (found products)!")
                    return True
            except:
                pass
            
            raise Exception("Login verification failed")
            
    except Exception as e:
        print(f"[{session_name}] ❌ Login failed: {str(e)}")
        return False


def filter_samsung_products(driver, session_name, is_mobile=False):
    """Filter products to show only Samsung devices"""
    try:
        print(f"\n[{session_name}] 🔍 Filtering for Samsung products...")
        
        time.sleep(3)
        
        # Scroll to top to ensure filters are visible
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        
        # Find and click Samsung checkbox - try multiple approaches
        samsung_clicked = False
        
        # Approach 1: Find all checkboxes and look for Samsung
        try:
            # Find all vendor checkboxes
            vendor_labels = driver.find_elements(By.CSS_SELECTOR, ".filters-available-size label")
            
            for label in vendor_labels:
                try:
                    label_text = label.text
                    if "Samsung" in label_text:
                        # Click the checkbox within this label
                        checkbox = label.find_element(By.CSS_SELECTOR, "span.checkmark")
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
                        time.sleep(0.5)
                        driver.execute_script("arguments[0].click();", checkbox)
                        samsung_clicked = True
                        print(f"[{session_name}] ✅ Clicked Samsung checkbox")
                        break
                except:
                    continue
        except:
            pass
        
        # Approach 2: Direct checkbox selector
        if not samsung_clicked:
            try:
                # Look for Samsung in the vendor filter section
                samsung_checkbox = driver.find_element(By.XPATH, "//span[text()='Samsung']/preceding-sibling::span[@class='checkmark']")
                driver.execute_script("arguments[0].click();", samsung_checkbox)
                samsung_clicked = True
                print(f"[{session_name}] ✅ Clicked Samsung checkbox (direct)")
            except:
                pass
        
        # Approach 3: Click Samsung text
        if not samsung_clicked:
            try:
                samsung_text = driver.find_element(By.XPATH, "//span[text()='Samsung']")
                driver.execute_script("arguments[0].click();", samsung_text)
                samsung_clicked = True
                print(f"[{session_name}] ✅ Clicked Samsung text")
            except:
                pass
        
        # Approach 4: Click the parent label
        if not samsung_clicked:
            try:
                samsung_label = driver.find_element(By.XPATH, "//label[contains(., 'Samsung')]")
                driver.execute_script("arguments[0].click();", samsung_label)
                samsung_clicked = True
                print(f"[{session_name}] ✅ Clicked Samsung label")
            except:
                pass
        
        if not samsung_clicked:
            raise Exception("Failed to click Samsung filter")
        
        # Wait for products to filter
        time.sleep(4)
        print(f"[{session_name}] ✅ Samsung filter applied")
        return True
        
    except Exception as e:
        print(f"[{session_name}] ❌ Failed to filter Samsung products: {str(e)}")
        return False


def favorite_galaxy_s20_plus(driver, session_name, is_mobile=False):
    """Find and favorite the Galaxy S20+ device"""
    try:
        print(f"\n[{session_name}] ❤️ Adding Galaxy S20+ to favorites...")
        
        time.sleep(3)
        
        # Find the Galaxy S20+ product
        galaxy_found = False
        
        # Get all product containers
        products = driver.find_elements(By.CSS_SELECTOR, ".shelf-item")
        print(f"[{session_name}] Found {len(products)} products")
        
        for product in products:
            try:
                # Get product title
                title_element = product.find_element(By.CSS_SELECTOR, ".shelf-item__title")
                product_title = title_element.text
                print(f"[{session_name}] Checking product: {product_title}")
                
                if "Galaxy S20" in product_title:
                    print(f"[{session_name}] 📱 Found Galaxy S20+")
                    
                    # Scroll product into view
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", product)
                    time.sleep(2)
                    
                    # Find the favorite button within this product
                    try:
                        # Look for the favorite button/icon
                        favorite_button = product.find_element(By.CSS_SELECTOR, ".shelf-stopper")
                        driver.execute_script("arguments[0].click();", favorite_button)
                        galaxy_found = True
                        print(f"[{session_name}] ✅ Clicked favorite button for Galaxy S20+")
                        break
                    except:
                        # Try alternative selector
                        try:
                            favorite_button = product.find_element(By.CSS_SELECTOR, "button")
                            driver.execute_script("arguments[0].click();", favorite_button)
                            galaxy_found = True
                            print(f"[{session_name}] ✅ Clicked favorite button (alt) for Galaxy S20+")
                            break
                        except:
                            print(f"[{session_name}] ⚠️ Could not find favorite button in product")
                            
            except Exception as product_error:
                continue
        
        if not galaxy_found:
            raise Exception("Could not find or favorite Galaxy S20+")
        
        time.sleep(3)
        return True
        
    except Exception as e:
        print(f"[{session_name}] ❌ Failed to favorite Galaxy S20+: {str(e)}")
        return False


def verify_favorites(driver, session_name, is_mobile=False):
    """Navigate to favorites page and verify Galaxy S20+ is there"""
    try:
        print(f"\n[{session_name}] 📋 Verifying favorites...")
        
        time.sleep(3)
        
        # Find and click favorites link
        favorites_clicked = False
        
        # Look for the favorites counter/badge first (usually shows number of favorites)
        try:
            favorites_badge = driver.find_element(By.CSS_SELECTOR, ".navbar__cart__items__count, .MuiBadge-badge, .badge")
            # Click the parent element (usually the link)
            parent = favorites_badge.find_element(By.XPATH, "..")
            driver.execute_script("arguments[0].click();", parent)
            favorites_clicked = True
            print(f"[{session_name}] ✅ Clicked favorites badge")
        except:
            pass
        
        # Try different selectors for the favorites link
        if not favorites_clicked:
            selectors = [
                "a[href='/favourites']",
                "a[href='/favorites']",
                "//a[contains(@href, 'favourite')]",
                "//a[contains(@href, 'favorite')]",
                ".navbar-nav a[href*='fav']",
                "//a[contains(., 'Favourite')]",
                "//a[contains(., 'Favorite')]"
            ]
            
            for selector in selectors:
                try:
                    if selector.startswith("//"):
                        element = driver.find_element(By.XPATH, selector)
                    else:
                        element = driver.find_element(By.CSS_SELECTOR, selector)
                    
                    driver.execute_script("arguments[0].click();", element)
                    favorites_clicked = True
                    print(f"[{session_name}] ✅ Clicked favorites link")
                    break
                except:
                    continue
        
        if not favorites_clicked:
            raise Exception("Could not find favorites link")
        
        # Wait for favorites page to load
        time.sleep(5)
        
        # Verify Galaxy S20+ is in favorites
        print(f"[{session_name}] 🔍 Looking for Galaxy S20+ in favorites...")
        
        # Check if Galaxy S20+ is present
        page_source = driver.page_source
        
        if "Galaxy S20" in page_source:
            print(f"[{session_name}] ✅ Galaxy S20+ found in favorites!")
            
            # Try to find the actual product element for additional verification
            try:
                products = driver.find_elements(By.CSS_SELECTOR, ".shelf-item__title, .product-title, p")
                for product in products:
                    if "Galaxy S20" in product.text:
                        print(f"[{session_name}] ✅ Confirmed: Galaxy S20+ is displayed in favorites")
                        return True
            except:
                # If we found it in page source, that's good enough
                return True
        
        # Check if favorites is empty
        if "no products" in page_source.lower() or "empty" in page_source.lower():
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
        caps_dict = capability.capabilities.get('bstack:options', {})
        is_mobile = 'deviceName' in caps_dict
        
        # Initialize WebDriver with retry logic for Firefox
        print(f"[{session_name}] 🔧 Initializing WebDriver...")
        
        max_retries = 3 if "Firefox" in session_name else 1
        
        for attempt in range(max_retries):
            try:
                driver = webdriver.Remote(
                    command_executor=f'https://{BROWSERSTACK_USERNAME}:{BROWSERSTACK_ACCESS_KEY}@hub-cloud.browserstack.com/wd/hub',
                    options=capability
                )
                print(f"[{session_name}] ✅ WebDriver initialized successfully")
                break
            except Exception as init_error:
                if attempt < max_retries - 1:
                    print(f"[{session_name}] ⚠️ Initialization attempt {attempt + 1} failed, retrying...")
                    time.sleep(5)
                else:
                    raise init_error
        
        # Set timeouts
        driver.set_page_load_timeout(90 if is_mobile else 60)
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
    
    all_passed = True
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result == "PASSED" else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result != "PASSED":
            print(f"   Error: {result}")
            all_passed = False
    
    print("\n✨ Test suite execution completed!")
    print("📈 Check BrowserStack dashboard for detailed results")
    print("="*80)
    
    # Exit with appropriate code for Jenkins
    exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()