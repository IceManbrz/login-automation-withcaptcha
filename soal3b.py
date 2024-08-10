import requests
from PIL import Image
from io import BytesIO
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from twocaptcha import TwoCaptcha

# Your 2Captcha API Key
API_KEY = '03f44f10f65327b7c38c4864ce8c7543'

# Initialize 2Captcha solver
solver = TwoCaptcha(API_KEY)

def get_captcha_solution(captcha_image_url):
    try:
        # Download the CAPTCHA image
        response = requests.get(captcha_image_url)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))

        # Convert image to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Save image temporarily
        img.save('captcha.jpg', 'JPEG')

        # Send CAPTCHA image to 2Captcha using the library's method
        result = solver.normal('captcha.jpg')
        if result['status'] == 1:
            return result['code']
        else:
            raise Exception(f"Error solving CAPTCHA: {result['request']}")
    except Exception as e:
        print(f"Error solving CAPTCHA: {e}")
        return ""

# Initialize WebDriver
driver = webdriver.Chrome()

try:
    # Navigate to the login page
    driver.get("https://tes123.kpntr.com/login_staff")

    # Wait for the email field to be visible and fill it in
    email_field = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//p[text()='E-Mail']/following-sibling::input"))
    )
    email_field.clear()
    email_field.send_keys("staff123321@yopmail.com")

    # Wait for the password field to be visible and fill it in
    password_field = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//p[text()='Password']/following-sibling::input"))
    )
    password_field.clear()
    password_field.send_keys("123321staff")

    # Wait for CAPTCHA image to be visible and get its URL
    captcha_image_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//img[starts-with(@src, 'https://tes123.kpntr.com/captcha/randomize')]"))
    )
    captcha_image_url = captcha_image_element.get_attribute('src')
    print(f"Captcha Image URL: {captcha_image_url}")

    # Solve CAPTCHA using 2Captcha
    captcha_solution = get_captcha_solution(captcha_image_url)
    print(f"Captcha Solution: {captcha_solution}")

    if captcha_solution:
        # Fill in CAPTCHA field
        captcha_field = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "4UkNVsL"))
        )
        captcha_field.clear()
        captcha_field.send_keys(captcha_solution)
    else:
        print("Failed to solve CAPTCHA. Exiting...")

    # Submit the form
    submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[text()='Masuk']"))
    )
    submit_button.click()

    # Wait for the next page to load (adjust this as necessary)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//element_you_expect_on_next_page"))
    )

    input("Login successful. Press Enter to close the browser...")

except Exception as e:
    print(f"An error occurred: {e}")
    driver.save_screenshot('error_screenshot.png')
    input("Press Enter to close the browser...")

finally:
    driver.quit()
