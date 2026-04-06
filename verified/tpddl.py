import base64
import os, json, time, random, string
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from captcha import *
from captcha.solver import solve_captcha_with_openai
from utils import *
from openai import OpenAI

def generate_random_email():
    """Generate a random email for form submission"""
    names = ["user", "test", "demo", "verify", "check"]
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{random.choice(names)}.{random_str}@gmail.com"

def extract_tpddl_data_from_screenshot(image_path, api_key):
    """Use OpenAI Vision to extract bill data from screenshot"""
    client = OpenAI(api_key=api_key)
    
    with open(image_path, "rb") as f:
        base64_image = base64.b64encode(f.read()).decode("utf-8")
    
    prompt = """Extract all payment details from this TPDDL electricity bill screenshot and return as JSON.
Look for fields like: CA Number, Consumer Name, Bill Date, Due Date, Amount, etc.
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
    print(f"OpenAI response: {result_text[:200]}...")
    
    if "```json" in result_text:
        result_text = result_text.split("```json")[1].split("```")[0].strip()
    elif "```" in result_text:
        result_text = result_text.split("```")[1].split("```")[0].strip()
    
    try:
        return json.loads(result_text)
    except json.JSONDecodeError:
        print(f"Failed to parse JSON, returning raw text")
        return {"raw_response": result_text}

def verify_tpddl(driver, ca_number, api_key, max_retries=3):
    wait = WebDriverWait(driver, 10)

    for attempt in range(1, max_retries + 1):
        print(f"\n---->>>>>>  Attempt {attempt} of {max_retries}...")
        try:
            driver.get("https://www.tatapower-ddl.com/billpay/paybillonline.aspx")

            image_path = extract_and_save_tpddl_captcha(driver)
            question = "Solve the expression shown in the CAPTCHA image two digits + two digits. Just return the final numeric answer."

            captcha_value = solve_captcha_with_openai(image_path, question, api_key)
            time.sleep(2)

            kno_input = wait.until(EC.presence_of_element_located((By.ID, "txtcano")))
            kno_input.clear()
            kno_input.send_keys(ca_number)

            # Generate random email
            email = generate_random_email()
            print(f"Using email: {email}")
            email_input = wait.until(EC.presence_of_element_located((By.ID, "txtemail")))
            email_input.clear()
            email_input.send_keys(email)

            captcha_input = wait.until(EC.presence_of_element_located((By.ID, "TxtImgVer")))
            captcha_input.clear()
            captcha_input.send_keys(captcha_value)

            view_button = wait.until(EC.element_to_be_clickable((By.ID, "btnpay")))
            view_button.click()

            time.sleep(5)
            
            # Screenshot payment-details element
            os.makedirs("screenshots", exist_ok=True)
            screenshot_path = f"screenshots/tpddl_{ca_number}.png"
            
            try:
                payment_elem = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "payment-details")))
                payment_elem.screenshot(screenshot_path)
                print(f"Screenshot saved: {screenshot_path}")
            except:
                driver.save_screenshot(screenshot_path)
                print(f"Full page screenshot saved: {screenshot_path}")
            
            # Extract data from screenshot using OpenAI Vision
            print("Extracting data from screenshot...")
            result = extract_tpddl_data_from_screenshot(screenshot_path, api_key)
            print(f"Extracted data: {result}")

            if not result:
                raise ValueError("Empty result returned, retrying...")

            os.makedirs("data", exist_ok=True)
            filepath = os.path.join("data", f"tpddl_{ca_number}.json")
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=4, ensure_ascii=False)

            print(f"TPDDL data saved to {filepath}")
            return result 

        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")

    print("All attempts failed.")
    return {"success": False, "error": "TPDDL verification failed after multiple attempts."}
