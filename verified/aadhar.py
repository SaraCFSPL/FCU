import json, os, time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from captcha import *
from captcha.solver import solve_captcha_with_openai


def verify_aadhar(driver, aadhar_number, api_key, max_retries=5):
    wait = WebDriverWait(driver, 10)

    for attempt in range(1, max_retries + 1):
        print(f"\n---->>>>>>  Attempt {attempt} of {max_retries}...")

        try:
            driver.get("https://myaadhaar.uidai.gov.in/check-aadhaar-validity/en")

            refresh_aadhar_captcha(driver)
            time.sleep(1)
            base64_img = extract_aadhar_captcha_image(driver)

            question = """Extract text from the captcha image in english language. Maintain the case of the text. It contains numbers [0-9], alphabets [A-Z] or [a-z] and captcha length is 6. """
            captcha_val = solve_captcha_with_openai(base64_img, question, api_key)
            time.sleep(1)

            aadhar_input = wait.until(EC.presence_of_element_located((By.NAME, "uid")))
            aadhar_input.clear()
            aadhar_input.send_keys(aadhar_number)

            captcha_input = wait.until(EC.presence_of_element_located((By.NAME, "captcha")))
            captcha_input.clear()
            captcha_input.send_keys(captcha_val)

            proceed_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//div[@class='auth-form__button-container']//button[contains(text(), 'Proceed')]")))
            proceed_button.click()

            time.sleep(5)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            container = soup.find("div", class_="check-aadhaar-validity-response__container")

            if container:
                response_data = {
                    "Status": container.find("span", class_="check-aadhaar-validity-response__cong").text.strip(),
                    "Verification": container.find("span", class_="check-aadhaar-validity-response__desc").text.strip(),
                }

                details = container.find_all("div", class_="verify-display-field")
                for detail in details:
                    label = detail.find("span", class_="verify-display-field__label").text.strip()
                    value = detail.find_all("span")[-1].text.strip()
                    response_data[label] = value

                # Optional: Save to file
                os.makedirs("data", exist_ok=True)
                json_filename = os.path.join("data", f"Aadhar_{aadhar_number}.json")
                with open(json_filename, "w", encoding="utf-8") as f:
                    json.dump(response_data, f, indent=4, ensure_ascii=False)

                print(f"Aadhaar verification data saved to '{json_filename}'")
                return {
                    "success": True,
                    "message": "Verification successful",
                    "data": response_data
                }

            else:
                print("CAPTCHA might be wrong, retrying...")

        except Exception as e:
            print(f" Attempt {attempt} failed with error: {e}")

    return {
        "success": False,
        "message": "All verification attempts failed. Please try again later.",
        "data": None
    }
