import os, time, json
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from captcha import *
from utils import *
from captcha.solver.openai_text_solver import solve_text_captcha_with_openai  

def verify_puvnl(driver, account_number, district, api_key, max_retries=3):
    wait = WebDriverWait(driver, 10)

    for attempt in range(1, max_retries + 1):
        print(f"Attempt {attempt} of {max_retries}")

        try:
            driver.get("https://consumer.uppcl.org/wss/pay_bill_home")
            refresh_puvnl_captcha(driver)
            image_path = extract_puvnl_captcha_image(driver)
            captcha_text = solve_tesseract_captcha(image_path)
            print(f"[DEBUG] Raw Tesseract Output: '{captcha_text}'")
            
            # after Tesseract step
            captcha_text_raw = solve_tesseract_captcha(image_path)
            print(f"[DEBUG] Raw Tesseract Output: '{captcha_text_raw}'")

            question = "Solve the expression in the CAPTCHA text and return only the numeric result."

            openai_response = solve_text_captcha_with_openai(captcha_text_raw, question, api_key)
            if not openai_response["success"]:
                print("[ERROR] OpenAI failed to process CAPTCHA")
                continue

            captcha_value = openai_response["captcha_text"]


            kno_input = wait.until(EC.presence_of_element_located((By.ID, "kno")))
            kno_input.clear()
            kno_input.send_keys(account_number)


            dropdown = wait.until(EC.element_to_be_clickable((By.ID, "mat-select-0")))
            dropdown.click()

            district_xpath = f"//div[contains(@class, 'country-container')]//span[normalize-space(text())='{district}']"

            district_element = wait.until(EC.element_to_be_clickable((By.XPATH, district_xpath)))
            district_element.click()

            captcha_input = wait.until(EC.presence_of_element_located((By.ID, "captchaInput")))
            captcha_input.clear()
            captcha_input.send_keys(captcha_value)

            view_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'View')]")))
            view_button.click()
            print("Clicked 'View' button.")

            time.sleep(10)


            soup = BeautifulSoup(driver.page_source, "html.parser")

            table = soup.find("table", {"class": "result-table"})
            if table:
                headers = [th.get_text(strip=True) for th in table.find("thead").find_all("b")]
                rows = []
                for tr in table.find("tbody").find_all("tr"):
                    cells = tr.find_all("td")
                    row_data = {headers[i]: cells[i].get_text(strip=True) for i in range(len(cells))}
                    rows.append(row_data)
                result = rows
            else:
                result = {}
                smart_form = soup.find("div", class_="smart-form")
                if smart_form:
                    for label in smart_form.find_all("span", class_="labelColor"):
                        text = label.get_text(strip=True)
                        val = label.find_next("div", class_="details")
                        if val:
                            result[text] = val.get_text(strip=True)
                        else:
                            input_val = label.find_next("input")
                            result[text] = input_val.get("value", "").strip() if input_val else None

            os.makedirs("data", exist_ok=True)
            path = os.path.join("data", f"puvnl_{account_number}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=4, ensure_ascii=False)

            print(f"PUVNL data saved to {path}")
            return result

        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")

    print("All attempts failed")
    return {"error": "Verification failed after retries"}
