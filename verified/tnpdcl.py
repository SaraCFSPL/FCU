import os
import json
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from captcha import *
from captcha.solver import solve_captcha_with_openai


def verify_tnpdcl(driver, consumer_number, api_key, max_retries=3):
    wait = WebDriverWait(driver, 10)

    for attempt in range(1, max_retries + 1):
        print(f"\n---->>>>>> Attempt {attempt} of {max_retries}...")

        try:
            driver.get("https://www.tnebnet.org/qwp/qpay")
            refresh_tnpdcl_captcha(driver)
            time.sleep(2)  # Wait after CAPTCHA refresh

            image_path = extract_tnpdcl_captcha_image(driver)

            question = """Extract text from the captcha image in english language. Maintain the case of the text. It contains numbers [0-9], alphabets [A-Z] or [a-z] and Dont Consider Space and total length of the text should be 6. """
            captcha_value = solve_captcha_with_openai(image_path, question, api_key)

            print(f"Extracted CAPTCHA: {captcha_value}")

            result = {}
            time.sleep(2)
            # 🧾 Step 1: Fill in Consumer Number
            consumer_input = wait.until(EC.presence_of_element_located((By.ID, "userName")))
            consumer_input.clear()
            consumer_input.send_keys(consumer_number)
            time.sleep(2)

            # Step 2: Fill in CAPTCHA
            captcha_input = wait.until(EC.presence_of_element_located((By.ID, "CaptchaID")))
            captcha_input.clear()
            captcha_input.send_keys(captcha_value)
            time.sleep(2)  # Added before submitting

            # 🧷 Step 3: Submit
            submit_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-primary.mb-3"))
            )
            submit_button.click()
            print("Clicked 'Submit' button.")

            # ⏳ Step 4: Wait for the data table to appear
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.billtable tbody")))
            except:
                print("Timeout: Result table not found.")
                continue

            # Step 5: Parse with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, "html.parser")
            tbody = soup.select_one("table.billtable tbody")

            if not tbody:
                print("<tbody> not found.")
                continue

            # Step 6: Extract key-value pairs dynamically
            rows = tbody.find_all("tr")
            for index, row in enumerate(rows):
                cols = row.find_all("td")
                if len(cols) == 2:
                    key = cols[0].get_text(strip=True).replace(":", "")
                    value = cols[1].get_text(strip=True)
                    if key and value:
                        result[key] = value
                else:
                    continue  # Skip spacer rows

            # Step 7: Save JSON
            os.makedirs("data", exist_ok=True)
            safe_consumer_number = consumer_number.replace("/", "_")
            json_path = os.path.join("data", f"tnpdcl_{safe_consumer_number}.json")

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=4, ensure_ascii=False)

            print(f"Data extracted and saved to: {json_path}")
            return result

        except Exception as e:
            print(f"Attempt {attempt} failed with error: {e}")

    print("All attempts failed for TNPCL.")
    return {"success": False, "error": "All retry attempts failed."}
