import os
import json
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from PIL import Image
from selenium import webdriver
import base64
from bs4 import BeautifulSoup
from captcha import *
from utils import *


def verify_bescom(driver, account_id, max_retries=3):
    wait = WebDriverWait(driver, 10)

    for attempt in range(1, max_retries + 1):
        print(f"\n---->>>>>> Attempt {attempt} of {max_retries}...")

        try:
            driver.get("https://www.bescom.co.in/bescom/main/quick-payment")
            # Refresh and extract CAPTCHA
            refresh_bescom_captcha(driver)
            image_path = extract_bescom_captcha_image(driver)
            captcha_value = solve_tesseract_captcha(image_path)
            print(f"Extracted CAPTCHA: {captcha_value}")

            # Fill in the form
            account_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[formcontrolname='accID']")))
            account_input.clear()
            account_input.send_keys(account_id)

            captcha_input = wait.until(EC.presence_of_element_located((By.ID, "cpatchaInput")))
            captcha_input.clear()
            captcha_input.send_keys(captcha_value)

            view_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Continue']")))
            view_button.click()
            print("Clicked 'View' button.")

            time.sleep(5)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            result = {}

            # Extract Account Info (Account ID, Name)
            account_info = soup.select(".mid-box .inner-content .data-text")
            if account_info:
                labels = ["Account ID", "Name"]
                for idx, data in enumerate(account_info):
                    result[labels[idx]] = data.get_text(strip=True)
                    print(f"Found {labels[idx]}: {data.get_text(strip=True)}")

            # Extract Form Data (Current Balance, Due Date, etc.)
            form_fields = soup.select(".fields .row.box-input .col")
            for field in form_fields:
                label_tag = field.find("label")
                input_tag = field.find("input")
                if label_tag and input_tag:
                    label = label_tag.get_text(strip=True).replace(":", "")
                    value = input_tag.get("value", "").strip() or input_tag.get("placeholder", "").strip()
                    if value:
                        result[label] = value
                        print(f"Found {label}: {value}")  # Debugging the extracted data

            # Extract Email Address (masked email if any) and Phone Type (masked phone number)
            email_field = soup.select_one("input[formcontrolname='email']")
            phone_type_field = soup.select_one("input[formcontrolname='phoneType']")
            if email_field:
                result["Email Address"] = email_field.get("value", "").strip() or email_field.get("placeholder", "").strip()
                print(f"Found Email Address: {result['Email Address']}")
            if phone_type_field:
                result["Phone Type"] = phone_type_field.get("value", "").strip() or phone_type_field.get("placeholder", "").strip()
                print(f"Found Phone Type: {result['Phone Type']}")

            # Create 'data' folder if it doesn't exist
            os.makedirs("data", exist_ok=True)

            # Save the extracted result to a JSON file
            account_number = result.get("Account ID", account_id)
            file_path = os.path.join("data", f"bescom_{account_number}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=4, ensure_ascii=False)

            print(f"Data saved to {file_path}")
            return result


        except Exception as e:
            print(f" Attempt {attempt} failed with error: {e}")

    print("All attempts failed for BESCOM.")
    return {"success": False, "error": "All retry attempts failed."}