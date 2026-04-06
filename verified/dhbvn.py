import time
import os
import json
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from captcha import *

def verify_dhbvn(driver, account_number, max_retries=3):
    wait = WebDriverWait(driver, 10)
    time.sleep(1)

    for attempt in range(1, max_retries + 1):
        print(f"---->>>>>>  Attempt {attempt} of {max_retries}...")

        try:
            driver.get("https://epayment.dhbvn.org.in/b2cViewReceiptList.aspx")
            time.sleep(3) 

            acc_input = wait.until(EC.presence_of_element_located((By.ID, "txtAcNo")))
            acc_input.clear()
            acc_input.send_keys(account_number)
            print("Entered Account Number.")

            proceed_button = wait.until(EC.element_to_be_clickable((By.ID, "btnsubmit")))
            proceed_button.click()
            print("Clicked 'Proceed' button.")
            
            time.sleep(5)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            response_data = {}

            form_groups = soup.find_all("div", class_="form-group")
            for group in form_groups:
                label_tag = group.find("label")
                input_tag = group.find(["input", "textarea"])

                if label_tag and input_tag:
                    label = label_tag.text.strip()
                    value = input_tag.get("value", "").strip() if input_tag.name == "input" else input_tag.text.strip()
                    response_data[label] = value

            table = soup.find("table", class_="table")
            if table:
                headers = [th.text.strip() for th in table.find_all("th")]
                rows = table.find_all("tr")[1:] 
                if rows:
                    cells = rows[0].find_all("td")
                    if cells:
                        row_data = {headers[i]: cells[i].text.strip() for i in range(len(cells))}
                        response_data["Receipt Table"] = row_data
                else:
                    print("No rows found in the table.")
            else:
                print("Table with class 'table' not found.")

            if response_data:
                os.makedirs("data", exist_ok=True)
                json_path = os.path.join("data", f"dhbvn_{account_number}.json")

                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(response_data, f, indent=4, ensure_ascii=False)

                print(f"DHBVN bill details saved to '{json_path}'.")

                return response_data

        except Exception as e:
            print(f"Error during attempt {attempt}: {str(e)}")
            continue

    return {"error": "DHBVN verification failed  attempts"}