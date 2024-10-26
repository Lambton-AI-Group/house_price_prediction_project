from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support import expected_conditions as EC

# Enhanced Chrome options to better avoid detection
chrome_options = Options()
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

# Set up the Chrome driver with options (assuming options are set up as before)
driver = webdriver.Chrome(options=chrome_options)

# Load the target page
driver.get("https://www.zoocasa.ca")

# Signing In with credentials
# Step 1
login_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "a.style_nav-btn__MPyL1[data-testid='loginHeader']"))
)
login_button.click()

# Step 2
email_input = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[data-testid="loginRegistrationEmailTextField"]'))
)
email_input.clear()
email_input.send_keys("meriyasusangeorge@gmail.com")

# Step 3
continue_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue')]"))
)
continue_button.click()

# Step 4
password_input = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[data-testid="passwordLoginModal"]'))
)
password_input.clear()
password_input.send_keys("lambtoncollege")

# Step 5
sign_in_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="signInButton"]'))
)
sign_in_button.click()
