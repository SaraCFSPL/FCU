from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
import json
from bs4 import BeautifulSoup
from utils import *
from captcha import *
from captcha.solver import solve_captcha_with_openai


def verify_stamp_rajasthan(driver, certificate_no, state, stamp, certificate_issued_date, api_key, max_retries=3):
    wait = WebDriverWait(driver, 10)
    
    for attempt in range(1, max_retries + 1):
        print(f"\n---->>>>>> Attempt {attempt} of {max_retries}...")

        try:
            driver.get("https://www.shcilestamp.com/eStampIndia/VerifyCertificate.es?rDoAction=VerifyCert")
            
            image_path  = extract_stamp_duty_captcha(driver)
            question = """Extract text from the captcha image after this text 'Your Verify Cert Session Id is ' in english language Give one Time Only. Maintain the case of the text. It contains numbers [0-9], alphabets [A-Z] or [a-z]. """
            captcha_value = solve_captcha_with_openai(image_path, question, api_key)

            if isinstance(captcha_value, dict) and "captcha_text" in captcha_value:
                captcha_value = captcha_value["captcha_text"]
            else:
                captcha_value = captcha_value

            print(f"Extracted CAPTCHA: {captcha_value}")
            
            state_dropdown = wait.until(EC.element_to_be_clickable((By.ID, "selState")))
            state_select = Select(state_dropdown)
            
            if isinstance(state, str):
                state_value = state.replace("_", "-")
                state_select.select_by_value(state_value)
                print(f"Selected state by value: {state_value}")
                time.sleep(3)
            else:
                print("No state provided")

            certificate_input = wait.until(EC.presence_of_element_located((By.ID, "certIdMand")))
            certificate_input.clear()
            certificate_input.send_keys(certificate_no)
            print("Entered Certificate_No.")
            time.sleep(2)

            if isinstance(stamp, str) and hasattr(StampDutyType, stamp):
                stamp_enum = getattr(StampDutyType, stamp)
            elif isinstance(stamp, StampDutyType):
                stamp_enum = stamp
            else:
                stamp_enum = None
                print(f"Warning: Invalid stamp duty type '{stamp}'")

            if stamp_enum:
                display_name = stamp_duty_display_names.get(stamp_enum)
                print(f"Looking for option with display name: {display_name}")
            else:
                display_name = None

            stamp_dropdown = wait.until(EC.element_to_be_clickable((By.ID, "stampDutyTypeMand")))
            select = Select(stamp_dropdown)
            time.sleep(2)

            for option in select.options:
                print(f"Value: {option.get_attribute('value')} | Text: {option.text}")

            if display_name:
                for option in select.options:
                    if display_name in option.text:
                        select.select_by_visible_text(option.text)
                        print(f"Selected by text matching: {option.text}")
                        break
                else:
                    value_to_select = stamp_enum.value if stamp_enum else None
                    if value_to_select:
                        select.select_by_value(value_to_select)
                        print(f"Selected by value: {value_to_select}")
            else:
                for i, option in enumerate(select.options):
                    if option.text.strip() and i > 0:
                        select.select_by_index(i)
                        print(f"Fallback selection by index: {i}, text: {option.text}")
                        break

            date_input = wait.until(EC.presence_of_element_located((By.ID, "certIssueDateMand")))
            date_input.clear()
            date_input.send_keys(certificate_issued_date)
            print("Entered Certificate_Issued_Date.")

            captcha_input = wait.until(EC.presence_of_element_located((By.ID, "searchjcaptcha")))
            captcha_input.clear()
            captcha_input.send_keys(captcha_value)
            print("Entered CAPTCHA.")

            verify_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='pVerify' and contains(@value, 'Verify')]")))
            verify_button.click()
            print("Clicked 'Verify' button.")

            time.sleep(5)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            data = {}

            certificate_table = soup.find('table', {'width': '550'})
            if certificate_table:
                rows = certificate_table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) == 3:
                        label = cells[0].get_text(strip=True)
                        value = cells[2].get_text(strip=True)
                        if label and value:
                            data[label] = value
            
            if data:
                with open(f'data/Rajasthan_rent_{certificate_no}.json', 'w', encoding='utf-8') as json_file:
                    json.dump(data, json_file, ensure_ascii=False, indent=4)
                print(f"Data scraped and saved to 'data/Rajasthan_rent_{certificate_no}.json'.")
                return data
            else:
                print(f"No data found after attempt {attempt}. Retrying...")

        except Exception as e:
            print(f"Error in attempt {attempt}: {str(e)}")
            if attempt == max_retries:
                print("Max retries reached. Exiting...")

    return {"error": "Verification failed after multiple attempts"}
