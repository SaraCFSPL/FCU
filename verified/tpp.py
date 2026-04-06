import os
import json
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def verify_tpp(driver, four1, four2, four3, max_retries=3):
    wait = WebDriverWait(driver, 10)
    account_number = four1 + four2 + four3
    file_path = os.path.join("data", f"tpp_{account_number}.json")

    for attempt in range(1, max_retries + 1):
        print(f"\n---->>>>>>  Attempt {attempt} of {max_retries}...")

        try:
            driver.get("https://pgi.billdesk.com/pgidsk/pgmerc/tatapwr/TATAPWRDetails.jsp")
            time.sleep(1)

            wait.until(EC.presence_of_element_located((By.ID, "txtAccount1"))).send_keys(four1)
            wait.until(EC.presence_of_element_located((By.ID, "txtAccount2"))).send_keys(four2)
            wait.until(EC.presence_of_element_located((By.ID, "txtAccount3"))).send_keys(four3)

            wait.until(EC.element_to_be_clickable((By.ID, "submitbtn"))).click()
            print("Clicked 'View' button.")

            time.sleep(5)
            soup = BeautifulSoup(driver.page_source, "html.parser")

            result = {}

            for tr in soup.find_all("tr"):
                td_tags = tr.find_all("td")
                if len(td_tags) == 2:
                    key = td_tags[0].text.strip()
                    value = td_tags[1].text.strip() if td_tags[1].text.strip() else ""
                    if key:
                        result[key] = value

            for input_tag in soup.find_all("input"):
                if input_tag.get("name") == "txtTxnAmount":
                    result["Amount to be Paid"] = input_tag.get("value", "")
                elif input_tag.get("id") == "txtMobile":
                    result["Mobile Number"] = input_tag.get("value", "")
                elif input_tag.get("id") == "txtEmail":
                    result["Email ID (Optional)"] = input_tag.get("value", "")

            if not result:
                raise ValueError("Empty result, retrying...")

            os.makedirs("data", exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=4, ensure_ascii=False)

            print(f"Data saved to {file_path}")
            return result

        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")

    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Deleted empty file: {file_path}")

    print("All attempts failed.")
    return {"success": False, "error": "TPL verification failed after multiple attempts."}