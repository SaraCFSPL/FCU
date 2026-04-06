import os
import time
import json
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def verify_pan(driver, pan_number, aadhar_number, max_retries=3):
    wait = WebDriverWait(driver, 10)

    for attempt in range(1, max_retries + 1):
        print(f"\n---->>>>>>  Attempt {attempt} of {max_retries}...")

        try:
            driver.get("https://eportal.incometax.gov.in/iec/foservices/#/pre-login/link-aadhaar-status")
            time.sleep(5)

            # Fill PAN
            pan_input = wait.until(EC.presence_of_element_located((By.ID, "mat-input-0")))
            pan_input.clear()
            pan_input.send_keys(pan_number)

            # Fill Aadhaar
            aadhar_input = wait.until(EC.presence_of_element_located((By.ID, "mat-input-1")))
            aadhar_input.clear()
            aadhar_input.send_keys(aadhar_number)

            # Submit
            submit_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[@aria-label='View Link Aadhaar Status']")))
            submit_button.click()

            time.sleep(5)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            modal = soup.find("div", id="linkAadhaarFailure_desc")
            response_data = {}

            if modal:
                message = modal.find("span").text.strip()
                response_data["Status"] = message
                words = message.split()
                for i, word in enumerate(words):
                    if word.upper() == "PAN":
                        response_data["PAN"] = words[i+1]
                    elif word.upper() == "AADHAAR":
                        response_data["Aadhaar"] = words[i+1]

                os.makedirs("data", exist_ok=True)
                filename = os.path.join("data", f"pan_{pan_number}.json")
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(response_data, f, indent=4, ensure_ascii=False)
                print(f"PAN-Aadhaar link status saved to: {filename}")
                return response_data

            else:
                print("Status modal not found, retrying...")

        except Exception as e:
            print(f" Attempt {attempt} failed with error: {e}")

    print("All attempts failed.")
    return None
