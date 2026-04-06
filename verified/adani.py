import os
import json
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def verify_adani(driver, CA_number, max_retries=5):
    wait = WebDriverWait(driver, 15)

    for attempt in range(1, max_retries + 1):
        print(f"\n---->>>>>>  Attempt {attempt} of {max_retries}...")

        try:
            driver.get("https://www.adanielectricity.com/")
            time.sleep(5)

            input_box = wait.until(EC.presence_of_element_located((By.ID, "caNumber")))
            input_box.clear()
            input_box.send_keys(CA_number)

            proceed_button = wait.until(EC.element_to_be_clickable((By.ID, "fetchBill")))
            proceed_button.click()

            # Wait for consumer-details to appear
            time.sleep(10)
            
            # Debug: Check if element exists
            try:
                consumer_details = driver.find_element(By.CSS_SELECTOR, "ul.consumer-details")
                print(f"Found consumer-details: {consumer_details.is_displayed()}")
            except Exception as e:
                print(f"consumer-details not found: {e}")
                # Take screenshot for debugging
                os.makedirs("screenshots", exist_ok=True)
                driver.save_screenshot(f"screenshots/adani_debug_{CA_number}.png")
                print(f"Screenshot saved for debugging")
            
            # Use JavaScript to extract data from consumer-details
            js_script = """
            var data = {};
            var consumerDetails = document.querySelector('ul.consumer-details');
            if (consumerDetails) {
                var caNum = consumerDetails.querySelector('strong.QACANumber');
                var consName = consumerDetails.querySelector('strong.QAConsumerName');
                var units = consumerDetails.querySelector('strong.QUnitConsumed');
                var billMonth = consumerDetails.querySelector('strong.QBillMonth');
                var totalBill = consumerDetails.querySelector('strong.QTBillAmount');
                var minPay = consumerDetails.querySelector('strong.QMinimumPayable');
                
                data['CA Number'] = caNum ? caNum.innerText.trim() : '';
                data['Consumer Name'] = consName ? consName.innerText.trim() : '';
                data['Units Consumed'] = units ? units.innerText.trim() : '';
                data['Bill Month'] = billMonth ? billMonth.innerText.trim() : '';
                data['Total Bill Amount'] = totalBill ? totalBill.innerText.replace('₹ ', '').trim() : '';
                data['Minimum Payable'] = minPay ? minPay.innerText.replace('₹ ', '').trim() : '';
            }
            
            // Get header data
            var payable = document.querySelector('span.QPayable');
            var dueDate = document.querySelector('p.QDuedate');
            data['Payable Amount'] = payable ? payable.innerText.trim() : '';
            data['Due Date'] = dueDate ? dueDate.innerText.replace('Due on ', '').trim() : '';
            
            return data;
            """
            
            data = driver.execute_script(js_script)
            print(f"Extracted data: {data}")
            
            # Validate data
            if not data.get("CA Number"):
                print("WARNING: CA Number not found, retrying...")
                continue

            os.makedirs("data", exist_ok=True)
            json_filename = os.path.join("data", f"aadani_{CA_number}.json")
            with open(json_filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            print(f"Bill data saved to '{json_filename}'")
            return data

        except Exception as e:
            print(f" Attempt {attempt} failed with error: {e}")

    print("All attempts failed.")
    return None
