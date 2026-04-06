import os, json, time, re, base64
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from captcha.extractor import refresh_apepdcl_captcha, extract_apepdcl_captcha
from captcha.solver import solve_captcha_with_openai
from openai import OpenAI

def extract_data_from_screenshot(image_path, api_key):
    """Use OpenAI Vision to extract bill data from screenshot"""
    client = OpenAI(api_key=api_key)
    
    with open(image_path, "rb") as f:
        base64_image = base64.b64encode(f.read()).decode("utf-8")
    
    prompt = """Extract the following fields from this APEPDCL electricity bill screenshot and return as JSON:
- Service Number (UKSCNO)
- Category
- Consumer Name
- Address
- Section Office
- ERO
- Service Release Date
- Bill Date
- Due Date
- Date of Disconnection

Return ONLY valid JSON with these exact keys. Example:
{
    "Service Number (UKSCNO)": "value",
    "Category": "value",
    "Consumer Name": "value",
    "Address": "value",
    "Section Office": "value",
    "ERO": "value",
    "Service Release Date": "value",
    "Bill Date": "value",
    "Due Date": "value",
    "Date of Disconnection": "value"
}"""

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
    # Extract JSON from response
    if "```json" in result_text:
        result_text = result_text.split("```json")[1].split("```")[0].strip()
    elif "```" in result_text:
        result_text = result_text.split("```")[1].split("```")[0].strip()
    
    return json.loads(result_text)

def verify_apepdcl(driver, scno, api_key, max_retries=3):
    wait = WebDriverWait(driver, 10)

    for attempt in range(1, max_retries + 1):
        print(f"\n---->>>>>>  Attempt {attempt} of {max_retries}...")

        try:
            driver.get("https://www.apeasternpower.com/viewBillDetailsMain")
            time.sleep(8)

            # Handle CAPTCHA
            refresh_apepdcl_captcha(driver)
            base64_img = extract_apepdcl_captcha(driver)
            question = "Extract text from the APEPDCL CAPTCHA image. Case-sensitive. [A-Z, a-z, 0-9]"
            captcha_val = solve_captcha_with_openai(base64_img, question, api_key)

            # Fill form
            wait.until(EC.presence_of_element_located((By.ID, "ltscno"))).send_keys(scno)
            wait.until(EC.presence_of_element_located((By.ID, "Billans"))).send_keys(captcha_val)
            wait.until(EC.element_to_be_clickable((By.ID, "Billsignin"))).click()
            print("Submitted SCNO and CAPTCHA")

            time.sleep(5)
            
            # Take screenshot
            os.makedirs("screenshots", exist_ok=True)
            screenshot_path = f"screenshots/apepdcl_{scno}.png"
            driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved: {screenshot_path}")
            
            # Extract data from screenshot using OpenAI Vision
            print("Extracting data from screenshot using OpenAI Vision...")
            result = extract_data_from_screenshot(screenshot_path, api_key)
            print(f"Extracted data: {result}")
            
            # Validate
            if not result or not result.get("Consumer Name"):
                print("No valid data extracted, CAPTCHA might be wrong, retrying...")
                continue

            # Save output
            os.makedirs("data", exist_ok=True)
            filepath = os.path.join("data", f"apepdcl_{scno}.json")
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=4, ensure_ascii=False)

            print(f"Data saved to: {filepath}")
            return result

        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")

    print("All attempts failed. No data returned.")
    return None
