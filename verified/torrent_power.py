import os
import json
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


def normalize_key(key):
    return key.lower().replace(" ", "_").replace(".", "").replace(":", "")


def verify_torrent_power(driver, service_number, city_flags, max_retries=3):
    wait = WebDriverWait(driver, 30)
    
    # Get the city marked as True
    selected_cities = [city for city, enabled in city_flags.items() if enabled]
    
    if not selected_cities:
        return {"success": False, "error": "No city selected. Set at least one city to true."}
    
    city = selected_cities[0]
    print(f"====== Searching in city: {city} ======")

    for attempt in range(1, max_retries + 1):
        print(f"\n---->>>>>>  Attempt {attempt} of {max_retries}...")

        try:
            os.makedirs("data", exist_ok=True)

            driver.get("https://connect.torrentpower.com/tplcp/index.php/crCustmast/quickpay")
            time.sleep(3)  # Quick load

            # Enter Service Number - try multiple selectors
            print("Looking for service number input...")
            input_box = None
            try:
                input_box = wait.until(EC.presence_of_element_located((By.ID, "CrCustmast_custno")))
            except:
                try:
                    input_box = driver.find_element(By.CSS_SELECTOR, "input[name*='custno']")
                except:
                    input_box = driver.find_element(By.CSS_SELECTOR, "input[type='text']")
            
            input_box.clear()
            input_box.send_keys(service_number)
            print(f"Entered service number: {service_number}")

            # Select City - try multiple selectors
            print("Looking for city dropdown...")
            city_dropdown = None
            try:
                city_dropdown = wait.until(EC.presence_of_element_located((By.ID, "Users_city")))
            except:
                try:
                    city_dropdown = driver.find_element(By.CSS_SELECTOR, "select[name*='city']")
                except:
                    city_dropdown = driver.find_element(By.CSS_SELECTOR, "select")
            
            city_select = Select(city_dropdown)
            cities = [option.text.strip() for option in city_select.options]
            print(f"Available cities: {cities}")

            if city not in cities:
                print(f" Error: '{city}' not found in dropdown.")
                return {"success": False, "error": f"City '{city}' not found in dropdown. Available: {cities}"}

            city_select.select_by_visible_text(city)
            print(f"Selected city: {city}")

            # Extract captcha text directly from element
            print("Looking for captcha...")
            try:
                captcha_elem = driver.find_element(By.CSS_SELECTOR, ".sc-bFvsHx.gQNKVg")
                captcha_text = captcha_elem.text.strip()
                print(f"Captcha text: {captcha_text}")
                
                # Solve math captcha (e.g., "4 + 1 =" -> 5)
                import re
                match = re.match(r'(\d+)\s*([+\-*/])\s*(\d+)\s*=', captcha_text)
                if match:
                    num1, op, num2 = int(match.group(1)), match.group(2), int(match.group(3))
                    if op == '+':
                        captcha_answer = str(num1 + num2)
                    elif op == '-':
                        captcha_answer = str(num1 - num2)
                    elif op == '*':
                        captcha_answer = str(num1 * num2)
                    elif op == '/':
                        captcha_answer = str(num1 // num2)
                    print(f"Captcha answer: {captcha_answer}")
                    
                    # Fill captcha input
                    captcha_input = driver.find_element(By.CSS_SELECTOR, ".sc-jYwrAs.hHNwcj")
                    captcha_input.clear()
                    captcha_input.send_keys(captcha_answer)
                else:
                    print(f"Could not parse captcha: {captcha_text}")
            except Exception as e:
                print(f"Captcha handling skipped: {e}")

            # Click Pay Now button
            print("Looking for Pay Now button...")
            paynow_btn = wait.until(EC.element_to_be_clickable((By.ID, "paynow")))
            driver.execute_script("arguments[0].click();", paynow_btn)
            print(" Clicked 'Pay Now' button.")

            time.sleep(3)
            
            # Extract data using JavaScript - handles styled-components
            js_script = """
            var data = {};
            // Find all spans and pair labels with values
            var allSpans = document.querySelectorAll('span');
            var labels = [];
            var values = [];
            
            allSpans.forEach(function(span) {
                var text = span.innerText.trim();
                // Check if it's a label (contains common label text)
                if (text.match(/Consumer name|Bill date|Service number|Billed units|Amount|Due date|Address|Category/i)) {
                    labels.push({elem: span, text: text});
                }
            });
            
            // For each label, get the next sibling span as value
            labels.forEach(function(label) {
                var nextSibling = label.elem.nextElementSibling;
                if (nextSibling && nextSibling.tagName === 'SPAN') {
                    var key = label.text.toLowerCase().replace(/ /g, '_');
                    data[key] = nextSibling.innerText.trim();
                }
            });
            
            return data;
            """
            
            extracted_data = driver.execute_script(js_script)
            print(f"Extracted data: {extracted_data}")
            
            # Validate
            if not extracted_data or len(extracted_data) < 2:
                print("No data extracted, retrying...")
                continue

            # Save JSON
            json_path = os.path.join("data", f"torrent_power_{service_number}.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(extracted_data, f, indent=4, ensure_ascii=False)

            print(f"Torrent Power data saved to '{json_path}'")
            return {"success": True, "data": extracted_data}

        except Exception as e:
            print(f" Attempt {attempt} failed with error: {e}")

    print("All attempts failed for Torrent Power.")
    return {"success": False, "error": "All attempts failed during Torrent Power verification."}
