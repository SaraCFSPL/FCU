import os
import json
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def verify_tgspdcl(driver, service_number, max_retries=3):
    wait = WebDriverWait(driver, 10)

    for attempt in range(1, max_retries + 1):
        print(f"\n---->>>>>>  Attempt {attempt} of {max_retries}...")

        try:
            driver.get("https://tgsouthernpower.org/onlinebillenquiry")

            # Step 1: Enter Unique Service Number
            input_box = wait.until(EC.presence_of_element_located((By.ID, "ukscno")))
            input_box.clear()
            input_box.send_keys(service_number)

            # Step 2: Trigger JavaScript manually
            driver.execute_script("validateServiceno();")
            print("Triggered 'validateServiceno()' via JavaScript.")

            # Step 3: Wait for data to load
            time.sleep(5)

            # Step 4: Parse HTML with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, "html.parser")
            table = soup.find("table", class_="table")

            if not table:
                print(" Table not found, possible CAPTCHA or input error. Retrying...")
                continue

            data = {}
            current_section = None

            for row in table.find_all("tr"):
                cols = row.find_all(["th", "td"])
                cols_text = [col.get_text(strip=True).replace(":", "") for col in cols if col.get_text(strip=True)]

                if len(cols) == 1 and cols[0].has_attr("colspan"):
                    current_section = cols_text[0]
                    data[current_section] = {}
                else:
                    target = data if not current_section else data[current_section]
                    for i in range(0, len(cols_text) - 1, 2):
                        key = cols_text[i]
                        value = cols_text[i + 1].replace("₹", "").strip()
                        target[key] = value

            # Step 5: Save data to JSON
            os.makedirs("data", exist_ok=True)
            json_path = os.path.join("data", f"tgspdcl_{service_number}.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            print(f"TGSPDCL data saved to '{json_path}'")
            return data

        except Exception as e:
            print(f" Attempt {attempt} failed with error: {e}")

    print("All attempts failed for TGSPDCL.")
