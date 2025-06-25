import os
import logging
import threading
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    WebDriverException,
    ElementClickInterceptedException
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webdriver import WebDriver
from dotenv import load_dotenv
import urllib3

# Suppress OpenSSL warnings
urllib3.disable_warnings(urllib3.exceptions.NotOpenSSLWarning)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_execution.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class TestConfig:
    """Centralized test configuration"""
    URL: str = "https://bstackdemo.com/"
    USERNAME: str = "demouser"
    PASSWORD: str = "testingisfun99"
    
    # Timeouts
    DEFAULT_TIMEOUT: int = 20
    LOGIN_TIMEOUT: int = 30
    PAGE_LOAD_TIMEOUT: int = 60
    MOBILE_PAGE_LOAD_TIMEOUT: int = 90
    
    # Retry settings
    MAX_INIT_RETRIES: int = 3
    RETRY_DELAY: int = 5
    
    # BrowserStack credentials
    BROWSERSTACK_USERNAME: str = os.getenv('BROWSERSTACK_USERNAME', '')
    BROWSERSTACK_ACCESS_KEY: str = os.getenv('BROWSERSTACK_ACCESS_KEY', '')
    
    def __post_init__(self):
        if not self.BROWSERSTACK_USERNAME or not self.BROWSERSTACK_ACCESS_KEY:
            raise ValueError("BrowserStack credentials not found in environment variables")


class BrowserStackCapabilities:
    """Factory class for creating BrowserStack capabilities"""
    
    @staticmethod
    def chrome_windows() -> Dict:
        """Create Chrome on Windows 10 capabilities"""
        return {
            'browserName': 'Chrome',
            'browserVersion': 'latest',
            'bstack:options': {
                'os': 'Windows',
                'osVersion': '10',
                'sessionName': 'Windows 10 Chrome Test',
                'buildName': 'BStackDemo Complete Test Suite',
                'projectName': 'E-commerce Full Flow Test',
                'debug': True,
                'networkLogs': True,
                'consoleLogs': 'verbose'
            }
        }
    
    @staticmethod
    def firefox_macos() -> Dict:
        """Create Firefox on macOS Ventura capabilities"""
        return {
            'browserName': 'Firefox',
            'browserVersion': 'latest',
            'bstack:options': {
                'os': 'OS X',
                'osVersion': 'Ventura',
                'sessionName': 'macOS Ventura Firefox Test',
                'buildName': 'BStackDemo Complete Test Suite',
                'projectName': 'E-commerce Full Flow Test',
                'debug': True,
                'networkLogs': True,
                'consoleLogs': 'verbose',
                'idleTimeout': 300,
                'acceptSslCerts': True,
                'acceptInsecureCerts': True
            }
        }
    
    @staticmethod
    def android_chrome() -> Dict:
        """Create Samsung Galaxy S22 capabilities"""
        return {
            'bstack:options': {
                'deviceName': 'Samsung Galaxy S22',
                'realMobile': True,
                'osVersion': '12.0',
                'browserName': 'chrome',
                'sessionName': 'Samsung Galaxy S22 Chrome Test',
                'buildName': 'BStackDemo Complete Test Suite',
                'projectName': 'E-commerce Full Flow Test',
                'debug': True,
                'networkLogs': True,
                'consoleLogs': 'verbose',
                'appiumVersion': '2.0.0'
            }
        }


class ElementInteractor:
    """Helper class for element interactions"""
    
    def __init__(self, driver: WebDriver, config: TestConfig):
        self.driver = driver
        self.config = config
        self.wait = WebDriverWait(driver, config.DEFAULT_TIMEOUT)
    
    def safe_click(self, locator: Tuple[str, str], description: str, 
                   timeout: Optional[int] = None, use_js: bool = False) -> bool:
        """Safely click an element with multiple strategies"""
        timeout = timeout or self.config.DEFAULT_TIMEOUT
        wait = WebDriverWait(self.driver, timeout)
        
        strategies = [
            self._standard_click if not use_js else self._js_click,
            self._js_click,
            self._action_chains_click
        ]
        
        for i, strategy in enumerate(strategies, 1):
            try:
                element = wait.until(EC.element_to_be_clickable(locator))
                strategy(element)
                logger.info(f"Successfully clicked {description} (strategy {i})")
                return True
            except (TimeoutException, NoSuchElementException, 
                    WebDriverException, ElementClickInterceptedException) as e:
                logger.warning(f"Click strategy {i} failed for {description}: {e}")
                if i < len(strategies):
                    time.sleep(1)
                continue
        
        logger.error(f"All click strategies failed for {description}")
        return False
    
    def _standard_click(self, element):
        """Standard click method"""
        element.click()
    
    def _js_click(self, element):
        """JavaScript click method"""
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.5)
        self.driver.execute_script("arguments[0].click();", element)
    
    def _action_chains_click(self, element):
        """ActionChains click method"""
        ActionChains(self.driver).move_to_element(element).click().perform()
    
    def wait_for_element(self, locator: Tuple[str, str], description: str, 
                        timeout: Optional[int] = None):
        """Wait for element to be present"""
        timeout = timeout or self.config.DEFAULT_TIMEOUT
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located(locator))
            logger.info(f"Found element: {description}")
            return element
        except TimeoutException:
            logger.error(f"Element not found: {description}")
            return None
    
    def select_dropdown_option(self, dropdown_id: str, option_text: str, 
                              description: str, is_mobile: bool = False) -> bool:
        """Enhanced dropdown selection for React Select components"""
        try:
            logger.info(f"Selecting {description}: {option_text}")
            
            # Click dropdown to open
            if not self._open_dropdown(dropdown_id, description):
                return False
            
            # Wait for dropdown to open
            time.sleep(3 if is_mobile else 2)
            
            # Select option using multiple strategies
            return self._select_option(option_text, description)
            
        except Exception as e:
            logger.error(f"Failed to select {description}: {e}")
            return False
    
    def _open_dropdown(self, dropdown_id: str, description: str) -> bool:
        """Open dropdown using multiple selectors"""
        selectors = [
            (By.ID, dropdown_id),
            (By.CSS_SELECTOR, f"#{dropdown_id}"),
            (By.CSS_SELECTOR, f"div#{dropdown_id}"),
            (By.XPATH, f"//div[@id='{dropdown_id}']")
        ]
        
        for selector in selectors:
            if self.safe_click(selector, f"{description} dropdown", use_js=True):
                return True
        
        logger.error(f"Could not open {description} dropdown")
        return False
    
    def _select_option(self, option_text: str, description: str) -> bool:
        """Select option from opened dropdown"""
        selection_strategies = [
            self._select_by_react_option,
            self._select_by_text_content,
            self._select_by_generic_selectors,
            self._select_first_available
        ]
        
        for strategy in selection_strategies:
            if strategy(option_text, description):
                time.sleep(1)
                return True
        
        logger.error(f"Could not select {option_text}")
        return False
    
    def _select_by_react_option(self, option_text: str, description: str) -> bool:
        """Select using React Select option elements"""
        try:
            option_elements = self.driver.find_elements(
                By.CSS_SELECTOR, "div[id*='react-select'][id*='option']"
            )
            
            for element in option_elements:
                if option_text in element.text or element.text == option_text:
                    self._js_click(element)
                    logger.info(f"Selected {option_text} from React options")
                    return True
        except Exception as e:
            logger.debug(f"React option selection failed: {e}")
        return False
    
    def _select_by_text_content(self, option_text: str, description: str) -> bool:
        """Select by text content"""
        try:
            xpath = f"//div[contains(text(), '{option_text}')]"
            elements = self.driver.find_elements(By.XPATH, xpath)
            
            for element in elements:
                if element.is_displayed():
                    self._js_click(element)
                    logger.info(f"Selected {option_text} by text")
                    return True
        except Exception as e:
            logger.debug(f"Text content selection failed: {e}")
        return False
    
    def _select_by_generic_selectors(self, option_text: str, description: str) -> bool:
        """Select using generic selectors"""
        selectors = [
            f"//div[@role='option'][contains(., '{option_text}')]",
            f"//div[@class='css-1n7v3ny-option'][contains(., '{option_text}')]",
            f"//div[contains(@class, 'option')][contains(., '{option_text}')]",
            f"//*[contains(., '{option_text}')][contains(@id, 'option')]"
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.XPATH, selector)
                self.driver.execute_script("arguments[0].click();", element)
                logger.info(f"Selected {option_text} using generic selector")
                return True
            except Exception:
                continue
        return False
    
    def _select_first_available(self, option_text: str, description: str) -> bool:
        """Fallback: select first available option"""
        try:
            first_option = self.driver.find_element(By.CSS_SELECTOR, "[id*='option-0']")
            self.driver.execute_script("arguments[0].click();", first_option)
            logger.warning(f"Selected first available option as fallback")
            return True
        except Exception:
            return False


class ECommerceTestSuite:
    """Main test suite class"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.test_results: Dict[str, str] = {}
        self.results_lock = threading.Lock()
    
    def create_driver(self, capabilities: Dict, session_name: str) -> Optional[WebDriver]:
        """Create WebDriver with retry logic"""
        max_retries = self.config.MAX_INIT_RETRIES if "Firefox" in session_name else 1
        
        for attempt in range(max_retries):
            try:
                logger.info(f"[{session_name}] Initializing WebDriver (attempt {attempt + 1})")
                
                driver = webdriver.Remote(
                    command_executor=f'https://{self.config.BROWSERSTACK_USERNAME}:'
                                   f'{self.config.BROWSERSTACK_ACCESS_KEY}@hub-cloud.browserstack.com/wd/hub',
                    desired_capabilities=capabilities
                )
                
                # Set timeouts
                is_mobile = 'deviceName' in capabilities.get('bstack:options', {})
                timeout = self.config.MOBILE_PAGE_LOAD_TIMEOUT if is_mobile else self.config.PAGE_LOAD_TIMEOUT
                
                driver.set_page_load_timeout(timeout)
                driver.implicitly_wait(10)
                
                logger.info(f"[{session_name}] WebDriver initialized successfully")
                return driver
                
            except Exception as e:
                logger.error(f"[{session_name}] Initialization attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(self.config.RETRY_DELAY)
                else:
                    raise e
        
        return None
    
    def login_to_site(self, driver: WebDriver, interactor: ElementInteractor, 
                     session_name: str, is_mobile: bool = False) -> bool:
        """Perform login to BStackDemo"""
        try:
            logger.info(f"[{session_name}] Starting login process")
            
            # Wait for initial page load
            time.sleep(5 if is_mobile else 3)
            
            # Click Sign In
            if not interactor.safe_click((By.ID, "signin"), "Sign In button", 
                                       timeout=self.config.LOGIN_TIMEOUT):
                raise Exception("Failed to click Sign In")
            
            time.sleep(5 if is_mobile else 3)
            
            # Select username and password
            if not interactor.select_dropdown_option("username", self.config.USERNAME, 
                                                   "username", is_mobile):
                raise Exception("Failed to select username")
            
            if not interactor.select_dropdown_option("password", self.config.PASSWORD, 
                                                   "password", is_mobile):
                raise Exception("Failed to select password")
            
            time.sleep(2)
            
            # Click login button
            if not interactor.safe_click((By.ID, "login-btn"), "Login button"):
                raise Exception("Failed to click login button")
            
            # Verify login success
            logger.info(f"[{session_name}] Waiting for login to complete")
            time.sleep(8 if is_mobile else 5)
            
            if self._verify_login_success(driver, session_name):
                logger.info(f"[{session_name}] Login successful")
                return True
            else:
                raise Exception("Login verification failed")
                
        except Exception as e:
            logger.error(f"[{session_name}] Login failed: {e}")
            return False
    
    def _verify_login_success(self, driver: WebDriver, session_name: str) -> bool:
        """Verify login was successful"""
        try:
            # Check for products shelf
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "shelf-container"))
            )
            return True
        except TimeoutException:
            # Alternative check: look for products
            try:
                products = driver.find_elements(By.CSS_SELECTOR, ".shelf-item")
                return len(products) > 0
            except Exception:
                return False
    
    def filter_samsung_products(self, driver: WebDriver, interactor: ElementInteractor, 
                              session_name: str, is_mobile: bool = False) -> bool:
        """Filter products to show only Samsung devices"""
        try:
            logger.info(f"[{session_name}] Filtering for Samsung products")
            
            time.sleep(3)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
            
            # Multiple strategies to find and click Samsung checkbox
            samsung_strategies = [
                self._click_samsung_checkbox_by_label,
                self._click_samsung_checkbox_direct,
                self._click_samsung_text,
                self._click_samsung_label
            ]
            
            for strategy in samsung_strategies:
                if strategy(driver, session_name):
                    time.sleep(4)
                    logger.info(f"[{session_name}] Samsung filter applied")
                    return True
            
            raise Exception("Failed to apply Samsung filter")
            
        except Exception as e:
            logger.error(f"[{session_name}] Failed to filter Samsung products: {e}")
            return False
    
    def _click_samsung_checkbox_by_label(self, driver: WebDriver, session_name: str) -> bool:
        """Click Samsung checkbox by finding labels"""
        try:
            vendor_labels = driver.find_elements(By.CSS_SELECTOR, ".filters-available-size label")
            for label in vendor_labels:
                if "Samsung" in label.text:
                    checkbox = label.find_element(By.CSS_SELECTOR, "span.checkmark")
                    driver.execute_script("arguments[0].click();", checkbox)
                    logger.info(f"[{session_name}] Clicked Samsung checkbox")
                    return True
        except Exception:
            pass
        return False
    
    def _click_samsung_checkbox_direct(self, driver: WebDriver, session_name: str) -> bool:
        """Click Samsung checkbox directly"""
        try:
            samsung_checkbox = driver.find_element(
                By.XPATH, "//span[text()='Samsung']/preceding-sibling::span[@class='checkmark']"
            )
            driver.execute_script("arguments[0].click();", samsung_checkbox)
            logger.info(f"[{session_name}] Clicked Samsung checkbox (direct)")
            return True
        except Exception:
            pass
        return False
    
    def _click_samsung_text(self, driver: WebDriver, session_name: str) -> bool:
        """Click Samsung text"""
        try:
            samsung_text = driver.find_element(By.XPATH, "//span[text()='Samsung']")
            driver.execute_script("arguments[0].click();", samsung_text)
            logger.info(f"[{session_name}] Clicked Samsung text")
            return True
        except Exception:
            pass
        return False
    
    def _click_samsung_label(self, driver: WebDriver, session_name: str) -> bool:
        """Click Samsung label"""
        try:
            samsung_label = driver.find_element(By.XPATH, "//label[contains(., 'Samsung')]")
            driver.execute_script("arguments[0].click();", samsung_label)
            logger.info(f"[{session_name}] Clicked Samsung label")
            return True
        except Exception:
            pass
        return False
    
    def favorite_galaxy_s20_plus(self, driver: WebDriver, session_name: str, 
                                is_mobile: bool = False) -> bool:
        """Find and favorite the Galaxy S20+ device"""
        try:
            logger.info(f"[{session_name}] Adding Galaxy S20+ to favorites")
            
            time.sleep(3)
            products = driver.find_elements(By.CSS_SELECTOR, ".shelf-item")
            logger.info(f"[{session_name}] Found {len(products)} products")
            
            for product in products:
                try:
                    title_element = product.find_element(By.CSS_SELECTOR, ".shelf-item__title")
                    product_title = title_element.text
                    
                    if "Galaxy S20" in product_title:
                        logger.info(f"[{session_name}] Found Galaxy S20+")
                        
                        # Scroll product into view
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", product)
                        time.sleep(2)
                        
                        # Find and click favorite button
                        if self._click_favorite_button(driver, product, session_name):
                            time.sleep(3)
                            return True
                            
                except Exception:
                    continue
            
            raise Exception("Could not find or favorite Galaxy S20+")
            
        except Exception as e:
            logger.error(f"[{session_name}] Failed to favorite Galaxy S20+: {e}")
            return False
    
    def _click_favorite_button(self, driver: WebDriver, product, session_name: str) -> bool:
        """Click favorite button for a product"""
        selectors = [".shelf-stopper", "button"]
        
        for selector in selectors:
            try:
                favorite_button = product.find_element(By.CSS_SELECTOR, selector)
                driver.execute_script("arguments[0].click();", favorite_button)
                logger.info(f"[{session_name}] Clicked favorite button for Galaxy S20+")
                return True
            except Exception:
                continue
        
        logger.warning(f"[{session_name}] Could not find favorite button")
        return False
    
    def verify_favorites(self, driver: WebDriver, interactor: ElementInteractor, 
                        session_name: str, is_mobile: bool = False) -> bool:
        """Navigate to favorites page and verify Galaxy S20+ is there"""
        try:
            logger.info(f"[{session_name}] Verifying favorites")
            
            time.sleep(3)
            
            # Find and click favorites link
            if not self._navigate_to_favorites(driver, session_name):
                raise Exception("Could not navigate to favorites")
            
            # Wait for favorites page to load
            time.sleep(5)
            
            # Verify Galaxy S20+ is in favorites
            return self._verify_galaxy_in_favorites(driver, session_name)
            
        except Exception as e:
            logger.error(f"[{session_name}] Failed to verify favorites: {e}")
            return False
    
    def _navigate_to_favorites(self, driver: WebDriver, session_name: str) -> bool:
        """Navigate to favorites page"""
        # Try favorites badge first
        try:
            favorites_badge = driver.find_element(
                By.CSS_SELECTOR, ".navbar__cart__items__count, .MuiBadge-badge, .badge"
            )
            parent = favorites_badge.find_element(By.XPATH, "..")
            driver.execute_script("arguments[0].click();", parent)
            logger.info(f"[{session_name}] Clicked favorites badge")
            return True
        except Exception:
            pass
        
        # Try direct favorites links
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
                logger.info(f"[{session_name}] Clicked favorites link")
                return True
            except Exception:
                continue
        
        return False
    
    def _verify_galaxy_in_favorites(self, driver: WebDriver, session_name: str) -> bool:
        """Verify Galaxy S20+ is in favorites"""
        logger.info(f"[{session_name}] Looking for Galaxy S20+ in favorites")
        
        page_source = driver.page_source
        
        if "Galaxy S20" in page_source:
            logger.info(f"[{session_name}] Galaxy S20+ found in favorites!")
            
            # Additional verification
            try:
                products = driver.find_elements(By.CSS_SELECTOR, ".shelf-item__title, .product-title, p")
                for product in products:
                    if "Galaxy S20" in product.text:
                        logger.info(f"[{session_name}] Confirmed: Galaxy S20+ is displayed in favorites")
                        return True
            except Exception:
                # Page source check was sufficient
                return True
        
        # Check if favorites is empty
        if any(term in page_source.lower() for term in ["no products", "empty"]):
            raise Exception("Favorites page is empty - product was not added")
        
        raise Exception("Galaxy S20+ not found in favorites")
    
    def run_complete_test(self, capabilities: Dict) -> bool:
        """Run the complete test flow"""
        driver = None
        session_name = capabilities.get('bstack:options', {}).get('sessionName', 'Unknown')
        
        try:
            logger.info(f"{'='*60}")
            logger.info(f"🚀 STARTING TEST: {session_name}")
            logger.info(f"{'='*60}")
            
            # Detect if mobile
            is_mobile = 'deviceName' in capabilities.get('bstack:options', {})
            
            # Initialize WebDriver
            driver = self.create_driver(capabilities, session_name)
            if not driver:
                raise Exception("Failed to initialize WebDriver")
            
            # Create element interactor
            interactor = ElementInteractor(driver, self.config)
            
            # Navigate to site
            logger.info(f"[{session_name}] Navigating to {self.config.URL}")
            driver.get(self.config.URL)
            
            # Execute test steps
            test_steps = [
                ("Login", lambda: self.login_to_site(driver, interactor, session_name, is_mobile)),
                ("Filter Samsung", lambda: self.filter_samsung_products(driver, interactor, session_name, is_mobile)),
                ("Favorite Galaxy S20+", lambda: self.favorite_galaxy_s20_plus(driver, session_name, is_mobile)),
                ("Verify Favorites", lambda: self.verify_favorites(driver, interactor, session_name, is_mobile))
            ]
            
            for step_name, step_func in test_steps:
                logger.info(f"[{session_name}] Executing step: {step_name}")
                if not step_func():
                    raise Exception(f"{step_name} failed")
            
            # Test successful
            logger.info(f"[{session_name}] 🎉 ALL TESTS PASSED!")
            
            # Mark test as passed in BrowserStack
            driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", '
                '"arguments": {"status":"passed", "reason": "All test steps completed successfully"}}'
            )
            
            # Store result
            with self.results_lock:
                self.test_results[session_name] = "PASSED"
            
            return True
            
        except Exception as e:
            logger.error(f"[{session_name}] ❌ TEST FAILED: {e}")
            
            # Mark test as failed in BrowserStack
            if driver:
                try:
                    driver.execute_script(
                        f'browserstack_executor: {{"action": "setSessionStatus", '
                        f'"arguments": {{"status":"failed", "reason": "{str(e)[:100]}"}}}}'
                    )
                except Exception:
                    pass
            
            # Store result
            with self.results_lock:
                self.test_results[session_name] = f"FAILED: {str(e)}"
            
            return False
            
        finally:
            if driver:
                logger.info(f"[{session_name}] Closing browser session")
                try:
                    driver.quit()
                except Exception:
                    pass
    
    def run_parallel_tests(self) -> bool:
        """Run tests in parallel across multiple browsers"""
        logger.info("\n" + "="*80)
        logger.info("🧪 BROWSERSTACK E-COMMERCE TEST SUITE")
        logger.info("📋 Test Requirements:")
        logger.info("   1. Login with demouser/testingisfun99")
        logger.info("   2. Filter products to show Samsung devices")
        logger.info("   3. Favorite the Galaxy S20+ device")
        logger.info("   4. Verify Galaxy S20+ appears in favorites")
        logger.info("\n🌐 Running on:")
        logger.info("   • Windows 10 Chrome")
        logger.info("   • macOS Ventura Firefox")
        logger.info("   • Samsung Galaxy S22")
        logger.info("="*80)
        
        # Create capabilities
        capabilities_list = [
            BrowserStackCapabilities.chrome_windows(),
            BrowserStackCapabilities.firefox_macos(),
            BrowserStackCapabilities.android_chrome()
        ]
        
        # Run tests in parallel
        threads = []
        
        for cap in capabilities_list:
            thread = threading.Thread(target=self.run_complete_test, args=(cap,))
            thread.start()
            threads.append(thread)
        
        # Wait for all tests to complete
        for thread in threads:
            thread.join()
        
        # Print summary
        return self._print_test_summary()
    
    def _print_test_summary(self) -> bool:
        """Print test results summary"""
        logger.info("\n" + "="*80)
        logger.info("📊 TEST RESULTS SUMMARY")
        logger.info("="*80)
        
        all_passed = True
        for test_name, result in self.test_results.items():
            status = "✅ PASSED" if result == "PASSED" else "❌ FAILED"
            logger.info(f"{test_name}: {status}")
            if result != "PASSED":
                logger.info(f"   Error: {result}")
                all_passed = False
        
        logger.info("\n✨ Test suite execution completed!")
        logger.info("📈 Check BrowserStack dashboard for detailed results")
        logger.info("="*80)
        
        return all_passed


def main():
    """Main execution function"""
    try:
        # Initialize configuration
        config = TestConfig()
        
        # Initialize test suite
        test_suite = ECommerceTestSuite(config)
        
        # Run parallel tests
        all_passed = test_suite.run_parallel_tests()
        
        # Exit with appropriate code for CI/CD
        exit(0 if all_passed else 1)
        
    except Exception as e:
        logger.error(f"Critical error in main execution: {e}")
        exit(1)


if __name__ == "__main__":
    main()