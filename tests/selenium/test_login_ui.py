import os

import pytest
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


BASE_URL = os.environ.get("TEST_BASE_URL", "http://localhost:5000")


@pytest.fixture()
def browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,900")

    try:
        driver = webdriver.Chrome(options=options)
    except WebDriverException as exc:
        pytest.skip(f"Chrome WebDriver is not available: {exc.msg}")

    driver.implicitly_wait(2)
    yield driver
    driver.quit()


def test_login_page_loads(browser):
    browser.get(f"{BASE_URL}/login")

    assert "Sign In" in browser.title
    assert "FitTrack" in browser.page_source


def test_sign_in_form_is_visible(browser):
    browser.get(f"{BASE_URL}/login")

    username = browser.find_element(By.ID, "username")
    password = browser.find_element(By.ID, "password")

    assert username.is_displayed()
    assert password.is_displayed()


def test_get_started_tab_opens_signup_form(browser):
    browser.get(f"{BASE_URL}/login")

    browser.find_element(By.ID, "tabSignUp").click()
    signup_panel = browser.find_element(By.ID, "panelSignUp")
    WebDriverWait(browser, 5).until(
        lambda driver: "auth-panel--hidden" not in signup_panel.get_attribute("class")
    )

    assert browser.find_element(By.ID, "new_username").is_enabled()
    assert browser.find_element(By.ID, "email").is_enabled()


def test_signup_enter_key_moves_to_next_field(browser):
    browser.get(f"{BASE_URL}/login")
    browser.find_element(By.ID, "tabSignUp").click()

    login_id = browser.find_element(By.ID, "new_username")
    login_id.send_keys("seleniumuser")
    login_id.send_keys(Keys.ENTER)

    active_element = browser.switch_to.active_element
    assert active_element.get_attribute("id") == "email"


def test_valid_login_redirects_to_profile(browser):
    browser.get(f"{BASE_URL}/login")

    browser.find_element(By.ID, "username").send_keys("franco")
    browser.find_element(By.ID, "password").send_keys("password123")
    browser.find_element(By.ID, "submit").click()

    WebDriverWait(browser, 5).until(EC.url_contains("/myprofile"))
    assert "/myprofile" in browser.current_url
