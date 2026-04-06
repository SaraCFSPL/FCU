
import os
import json
import time
from PIL import Image
import pytesseract
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from captcha import *
from captcha.solver import solve_captcha_with_openai
from utils import *


ALL_COMPANY_CODES = ["DGVCL", "MGVCL", "PGVCL", "UGVCL"]

def verify_all_gvcl(driver, consumer_number, company_flags, api_key, max_retries=3):
    wait = WebDriverWait(driver, 10)
    
    # Get list of companies marked as True
    company_codes_to_try = [code for code, enabled in company_flags.items() if enabled]
    
    if not company_codes_to_try:
        return {"error": "No company selected. Set at least one company to true."}
    
    for code in company_codes_to_try:
        print(f"\n====== Trying company: {code} ======")
        
        for attempt in range(1, max_retries + 1):
            print(f"\n---->>>>>> Attempt {attempt} of {max_retries}...")

            try:
                driver.maximize_window()
                driver.get("https://mpay.guvnl.in/paytm/QuickPay.php")
        
                select_company(driver, code)
                image_path = extract_GVCL_captcha_image(driver)

                # Enter consumer number
                consumer_input = wait.until(EC.presence_of_element_located((By.ID, "consnumber")))
                consumer_input.clear()
                consumer_input.send_keys(consumer_number)

                # Solve CAPTCHA
                question = "Solve the shown in the CAPTCHA image. Just return the exact values containing [A-Z][a-z][0-9] in any order"
                captcha_value = solve_captcha_with_openai(image_path, question, api_key)

                captcha_input = wait.until(EC.presence_of_element_located((By.ID, "cap_code")))
                captcha_input.clear()
                captcha_input.send_keys(captcha_value)

                # Click submit
                proceed_button = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//input[@type='submit' and contains(@value, 'Check Consumer No.')]")
                ))
                proceed_button.click()

                time.sleep(1)

                # Capture detail div
                detail_div = wait.until(EC.presence_of_element_located((By.ID, "detailconsnumber")))
                time.sleep(2)

                os.makedirs("screenshots", exist_ok=True)
                screenshot_path = f"screenshots/{consumer_number}_detail.png"
                detail_div.screenshot(screenshot_path)

                # OCR the image
                img = Image.open(screenshot_path)
                ocr_text = pytesseract.image_to_string(img)

                # Extract and save data
                response_data = extract_gvcl_details_from_text(ocr_text)
                os.makedirs("data", exist_ok=True)
                json_filename = f"data/all_gvcl_{code}_{consumer_number}.json"
                with open(json_filename, "w", encoding="utf-8") as json_file:
                    json.dump(response_data, json_file, indent=4, ensure_ascii=False)
                print(f"Extracted data saved to: {json_filename}")

                # Check if Consumer Name is valid (not null or "CONSUMER NO")
                consumer_name = response_data.get("Consumer Name")
                if consumer_name and consumer_name.strip().upper() != "CONSUMER NO":
                    print(f" Valid Consumer Name found with {code}.")
                    return response_data
                else:
                    print(f"Invalid Consumer Name: '{consumer_name}'. Retrying...")
                    if os.path.exists(json_filename):
                        os.remove(json_filename)
                    time.sleep(2)

            except Exception as e:
                print(f" Attempt {attempt} failed with error: {e}")
                time.sleep(2)
        
        print(f"All attempts failed for {code}, trying next company...")

    print("All attempts failed for all companies.")
    return {"error": "Verification failed for all company codes"}