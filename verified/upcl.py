import os
import json
import time
import base64
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from captcha import *
from utils import *
from openai import OpenAI

def extract_upcl_data_from_screenshot(image_path, api_key):
    """Use OpenAI Vision to extract bill data from screenshot"""
    client = OpenAI(api_key=api_key)
    
    with open(image_path, "rb") as f:
        base64_image = base64.b64encode(f.read()).decode("utf-8")
    
    prompt = """Extract all bill details from this UPCL electricity bill screenshot and return as JSON.
Look for fields like: Account No, Consumer Name, Address, Bill Date, Due Date, Amount, etc.
Return ONLY valid JSON with the field names as keys."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                ]
            }
        ],
        max_tokens=500
    )
    
    result_text = response.choices[0].message.content.strip()
    if "```json" in result_text:
        result_text = result_text.split("```json")[1].split("```")[0].strip()
    elif "```" in result_text:
        result_text = result_text.split("```")[1].split("```")[0].strip()
    
    return json.loads(result_text)

def verify_upcl(driver, account_number, api_key, max_retries=3):
    wait = WebDriverWait(driver, 10)

    for attempt in range(1, max_retries + 1):
        print(f"\nAttempt {attempt} of {max_retries}...")

        try:
            driver.get("https://www.upcl.org/wss/viewBill")
            time.sleep(3)

            # Step 1: Refresh and extract CAPTCHA
            refresh_upcl_captcha(driver)
            image_path = extract_upcl_captcha_image(driver)
            captcha_value = solve_tesseract_captcha(image_path)

            # Step 2: Fill in the Account Number
            account_input = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[placeholder='Enter Service Connection / Account Number']")))
            account_input.clear()
            account_input.send_keys(account_number)

            # Step 3: Fill in CAPTCHA
            captcha_input = wait.until(EC.presence_of_element_located((By.ID, "cpatchaInput")))
            captcha_input.clear()
            captcha_input.send_keys(captcha_value)

            # Step 4: Submit
            submit_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[normalize-space()='Submit']")))
            submit_button.click()
            print("Clicked 'Submit' button.")

            # Step 5: Wait for mat-card-content and take screenshot
            time.sleep(5)
            
            os.makedirs("screenshots", exist_ok=True)
            screenshot_path = f"screenshots/upcl_{account_number}.png"
            
            try:
                # Try to find mat-card-content and screenshot it
                card_content = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "mat-card-content")))
                card_content.screenshot(screenshot_path)
                print(f"Screenshot saved: {screenshot_path}")
            except:
                # Fallback to full page screenshot
                driver.save_screenshot(screenshot_path)
                print(f"Full page screenshot saved: {screenshot_path}")
            
            # Step 6: Extract data from screenshot using OpenAI Vision
            print("Extracting data from screenshot...")
            result = extract_upcl_data_from_screenshot(screenshot_path, api_key)
            print(f"Extracted data: {result}")

            # Step 7: Save the result to a JSON file
            if result:
                os.makedirs("data", exist_ok=True)
                safe_account = str(result.get("Account No", account_number)).replace("/", "_")
                file_path = os.path.join("data", f"upcl_{safe_account}.json")

                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=4, ensure_ascii=False)

                print(f"Data saved to {file_path}")
                return result
            else:
                print("No data extracted, retrying...")

        except Exception as e:
            print(f"Attempt {attempt} failed with error: {e}")

    print("All attempts failed for UPCL.")
    return {"success": False, "error": "All retry attempts failed."}
