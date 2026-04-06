import os
import time
import json
import re
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from captcha import *
from utils import *
from captcha.solver import solve_captcha_with_openai



def verify_dvvnl(driver, account_number, district, api_key, max_retries: int = 5):
    wait = WebDriverWait(driver, 10)

    for attempt in range(1, max_retries + 1):
        print(f"\n---->>>>>>  Attempt {attempt} of {max_retries}...")


        try:
            driver.get("https://www.uppclonline.com/dispatch/Portal/appmanager/uppcl/wss?_nfpb=true&_pageLabel=uppcl_billInfo_payBill_home&pageID=PB_1010")
            refresh_dvvnl_captcha(driver)
            base64_img = extract_dvvnl_captcha_image(driver)

            # Define the instruction/question for OpenAI
            question = "Solve the expression shown in the CAPTCHA image. Just return the final numeric answer."

            # Pass the correct values to the solver
            captcha_value = solve_captcha_with_openai(base64_img, question, api_key)

            # Fill Account Number (KNO)
            kno_input = wait.until(EC.presence_of_element_located((By.ID, "kno")))
            kno_input.clear()
            kno_input.send_keys(account_number)

            # Select District
            dropdown = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "dropbtn")))
            dropdown.click()
            options = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@id='myDropdown']//a")))

            matched = False
            for option in options:
                if option.text.strip().lower() == district.strip().lower():
                    driver.execute_script("arguments[0].click();", option)
                    matched = True
                    break

            if not matched:
                raise Exception(f"District '{district}' not found.")

            # Enter CAPTCHA
            captcha_input = wait.until(EC.presence_of_element_located((By.ID, "verifyCode")))
            captcha_input.clear()
            captcha_input.send_keys(captcha_value)

            # Submit
            view_button = wait.until(EC.element_to_be_clickable((By.ID, "viewBt")))
            view_button.click()

            time.sleep(5)
            soup = BeautifulSoup(driver.page_source, "html.parser")

            result = {}
            for input_tag in soup.find_all("input", {"class": "formtxtField"}):
                value = input_tag.get("value", "").strip()
                label_td = input_tag.find_parent("td").find_previous_sibling("td")
                label = label_td.get_text(strip=True).replace(":", "") if label_td else "Unknown"
                if label and value:
                    result[label] = value

            # Extract KNO from URL
            view_bill_link = soup.find("a", class_="btnq")
            kno_match = re.search(r'portletInstance_billInfo_payBillHome_payBillHomekno=(\d+)', view_bill_link["href"])
            acc_no = kno_match.group(1) if kno_match else account_number

            os.makedirs("data", exist_ok=True)
            path = os.path.join("data", f"dvvnl_{acc_no}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=4, ensure_ascii=False)

            print(f"DVVNL data saved to '{path}'")
            return

        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")

    print("All attempts failed")
