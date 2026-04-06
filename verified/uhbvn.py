import os
import json
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils import *
from captcha import *

def verify_uhbvn(driver, account_number, max_retries=3):
    wait = WebDriverWait(driver, 15)
    
    driver.get("https://epayment.uhbvn.org.in/b2cpaybilladvance.aspx")
    
    # Wait for account input field to be ready
    acc_input = wait.until(EC.presence_of_element_located((By.ID, "txtacntnumber")))
    print("Page loaded, starting to fill details...")

    for attempt in range(1, max_retries + 1):
        print(f"---->>>>>>  Attempt {attempt} of {max_retries}...")
        try:
            # Extract captcha text
            captcha_value = extract_uhbvn_captcha(driver)
            print(f"Captcha value: {captcha_value}")

            # Fill account number
            acc_input = wait.until(EC.presence_of_element_located((By.ID, "txtacntnumber")))
            acc_input.clear()
            acc_input.send_keys(account_number)
            print(f"Entered account number: {account_number}")

            # Fill captcha
            captcha_input = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "captcha")))
            captcha_input.clear()
            captcha_input.send_keys(captcha_value)
            print(f"Entered captcha: {captcha_value}")

            # Click submit
            proceed_button = wait.until(EC.element_to_be_clickable((By.ID, "btnsubmit")))
            driver.execute_script("arguments[0].click();", proceed_button)
            print("Clicked submit button")

            time.sleep(5)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            response_data = {}

            form_groups = soup.find_all("div", class_="form-group")
            for group in form_groups:
                label_tag = group.find("label")
                input_tag = group.find(["input", "textarea"])
                if label_tag and input_tag:
                    label = label_tag.text.strip()
                    value = input_tag.get("value", "").strip() if input_tag.name == "input" else input_tag.text.strip()
                    response_data[label] = value

            if response_data:
                os.makedirs("data", exist_ok=True)
                json_path = os.path.join("data", f"uhbvn_{account_number}.json")
                print(f"File {json_path}  Successfully extracted.")

                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(response_data, f, indent=4, ensure_ascii=False)
                return response_data

        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            continue

    return {"error": "UHBVN verification failed after multiple attempts"}