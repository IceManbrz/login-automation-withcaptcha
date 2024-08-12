import requests
from PIL import Image
from io import BytesIO
import pytesseract
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import cv2
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary_image = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    inverted_image = cv2.bitwise_not(binary_image)
    return inverted_image

def get_captcha_solution(captcha_element):
    try:
        captcha_screenshot = captcha_element.screenshot_as_png
        image = Image.open(BytesIO(captcha_screenshot))

        image_array = np.array(image)

        preprocessed_image = preprocess_image(image_array)
        
        img = Image.fromarray(preprocessed_image)

        img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)

        captcha_text = pytesseract.image_to_string(img, config='--psm 7 --oem 3 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
        captcha_text = captcha_text.strip().replace(" ", "")  

        print(f"Raw Captcha OCR Output: {captcha_text}")

        if captcha_text:
            return captcha_text
        else:
            raise Exception("Error solving CAPTCHA: No text found")
    except Exception as e:
        print(f"Error solving CAPTCHA: {e}")
        return ""

driver = webdriver.Chrome()

try:
    driver.get("https://tes123.kpntr.com/login_staff")

    email_field = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//p[text()='E-Mail']/following-sibling::input"))
    )
    email_field.clear()
    email_field.send_keys("staff123321@yopmail.com")

    password_field = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//p[text()='Password']/following-sibling::input"))
    )
    password_field.clear()
    password_field.send_keys("123321staff")

    captcha_image_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//div[@id='myCaptcha']/img"))
    )

    captcha_solution = get_captcha_solution(captcha_image_element)
    print(f"Captcha Solution: {captcha_solution}")

    if captcha_solution:
        captcha_field = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//div[@id='myCaptcha']//following::input[1]"))
        )

        captcha_field.clear()

        driver.execute_script("arguments[0].value = arguments[1];", captcha_field, captcha_solution)
        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", captcha_field)

        time.sleep(1)

        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Masuk']"))
        )
        submit_button.click()
    else:
        print("Failed to solve CAPTCHA. Exiting...")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//element_you_expect_on_next_page"))
    )

    input("Login successful. Press Enter to close the browser...")

except Exception as e:
    print(f"An error occurred: {e}")
    input("Press Enter to close the browser...")

finally:
    driver.quit()
