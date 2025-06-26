import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_add_to_favorite(selenium):


    selenium.get("https://bstackdemo.com/")

    wait = WebDriverWait(selenium, 60)

    # Click "Sign In"
    wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Sign In"))).click()

    # Click "Select Username"
    wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(text(),'Select Username')]")))
    username_divs = selenium.find_elements(By.XPATH, "//div[contains(text(),'Select Username')]")
    if len(username_divs) > 2:
        username_divs[2].click()
    else:
        username_divs[0].click()  # fallback

    # Click "demouser"
    wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='demouser']"))).click()

    # Click "Select Password"
    wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Select Password']"))).click()

    # Click "testingisfun99"
    wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='testingisfun99']"))).click()

    # Click "Log In"
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Log In']"))).click()

    # Click "Samsung"
    wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Samsung']"))).click()

    # Click delete button for product with id="11"
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#11 button[aria-label="delete"]'))).click()

    # Click "Favourites"
    wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Favourites"))).click()

    # Assert that Galaxy S20+ image is displayed
    assert wait.until(EC.presence_of_element_located((By.XPATH, "//img[@alt='Galaxy S20+']"))).is_displayed(), "Galaxy S20+ image is not displayed"