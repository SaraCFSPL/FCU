import os
import time
import json
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from captcha import *
from utils import *
from captcha.solver import solve_captcha_with_openai


def verify_maharashtra(driver, consumer_number, api_key, max_retries=3):
    wait = WebDriverWait(driver, 10)

    for attempt in range(1, max_retries + 1):
        print(f"Attempt {attempt} of {max_retries}")

        try:
            driver.get("https://wss.mahadiscom.in/wss/wss?uiActionName=getViewPayBill")

            refresh_maha_captcha(driver)
            image_path = extract_maha_captcha_image(driver)

            try:
                # First try solving with Tesseract
                captcha_value = solve_tesseract_captcha(image_path)
                if not captcha_value or not captcha_value.strip():
                    raise ValueError("Empty CAPTCHA from Tesseract")
            except Exception as e:
                print(f"Tesseract CAPTCHA failed: {e}")
                # Fallback to OpenAI
                base64_img = extract_maha_captcha_image(driver)
                question = "Solve the expression in the CAPTCHA image and return only the numeric result."
                captcha_value = solve_captcha_with_openai(base64_img, question, api_key)

            consumer_input = wait.until(EC.presence_of_element_located((By.ID, "consumerNo")))
            consumer_input.clear()
            consumer_input.send_keys(consumer_number)

            captcha_input = wait.until(EC.presence_of_element_located((By.ID, "txtInput")))
            captcha_input.clear()
            captcha_input.send_keys(captcha_value)

            submit_click_script = """
            const submitSpan = document.getElementById("lblSubmit");
            if (submitSpan) {
                submitSpan.click();
                return true;
            }
            return false;
            """
            if not driver.execute_script(submit_click_script):
                raise Exception("Submit button not found")

            time.sleep(5)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            table = soup.find("table", {"id": "billingTable"})

            if not table:
                raise Exception("Billing table not found")

            header_row = table.find("tr", class_="head")
            header_cells = header_row.find_all("td")
            headers = []
            for td in header_cells:
                span = td.find("span")
                text = span.get_text(strip=True) if span else td.get_text(strip=True)
                headers.append(text or "Unknown")

            data_rows = []
            for row in table.find_all("tr", class_="tr_odd"):
                cells = row.find_all("td")
                row_data = {}
                for i in range(min(len(cells), len(headers))):
                    cell = cells[i]
                    img = cell.find("img")
                    if img:
                        row_data[headers[i]] = {
                            "src": img.get("src"),
                            "onclick": img.get("onclick"),
                            "title": img.get("title")
                        }
                    else:
                        row_data[headers[i]] = cell.get_text(strip=True)
                data_rows.append(row_data)

            os.makedirs("data", exist_ok=True)
            path = os.path.join("data", f"Maharashtra_{consumer_number}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data_rows, f, indent=4, ensure_ascii=False)

            print(f"Maharashtra data saved to '{path}'")
            return data_rows

        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")

    print("All attempts failed for Maharashtra Electricity")
    return {"error": "Verification failed after retries"}
