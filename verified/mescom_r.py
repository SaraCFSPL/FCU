import os
import json
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def verify_mescom_r(driver, consumer_no, max_retries=3):
    for attempt in range(1, max_retries + 1):
        print(f"\n---->>>>>>  Attempt {attempt} of {max_retries}...")
        try:
            wait = WebDriverWait(driver, 10)
            driver.get("https://mescomruralpayment.mesco.in/")
            time.sleep(1)
            kno_input = wait.until(EC.presence_of_element_located((By.ID, "txtConnectionID")))
            kno_input.clear()
            kno_input.send_keys(consumer_no)

            view_button = wait.until(EC.element_to_be_clickable((By.ID, "BtnPayment")))
            view_button.click()

            time.sleep(5)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            result = {}

            td_elements = soup.find_all("tr")
            for tr in td_elements:
                td_tags = tr.find_all("td")
                if len(td_tags) == 2:
                    key = td_tags[0].text.strip()
                    value = td_tags[1].text.strip() if td_tags[1].text.strip() else ""
                    if key:
                        result[key] = value

            input_elements = soup.find_all("input")
            for input_tag in input_elements:
                name = input_tag.get("name", "")
                val = input_tag.get("value", "")
                if name == "txtsubdiv":
                    result["SubDivision"] = val
                elif name == "txtphno":
                    result["Mobile No"] = val
                elif name == "txtRRNO":
                    result["RRNo"] = val
                elif name == "txtemailid":
                    result["Email ID"] = val
                elif name == "txtConnectionID":
                    result["Consumer ID"] = val
                elif name == "txtBillTotal":
                    result["Bill Amount (in Rs.)"] = val
                elif name == "txtPayment":
                    result["Payment (in Rs.)"] = val

            span_elements = soup.find_all("span")
            for span_tag in span_elements:
                if span_tag.get("id") == "lblCustomerName":
                    result["Consumer Name"] = span_tag.find_next("textarea").text.strip() if span_tag.find_next("textarea") else ""
                elif span_tag.get("id") == "lblPaymentChannel":
                    payment_channel = span_tag.find_next("table")
                    if payment_channel:
                        payment_option = payment_channel.find("input", {"type": "radio", "checked": "checked"})
                        result["Payment Channel"] = payment_option.get("value", "") if payment_option else "Unknown"

            if result.get("Consumer ID") or result.get("Consumer Name"):
                os.makedirs("data", exist_ok=True)
                file_path = os.path.join("data", f"mescom_r_{consumer_no}.json")
                print(f"File {file_path}  Successfully extracted.")

                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=4, ensure_ascii=False)
                return result

        except Exception:
            pass

        time.sleep(2)
    return {"error": "MESCOM-R verification failed after multiple attempts"}
