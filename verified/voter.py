import os
import json
import time
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from captcha import *
from captcha.solver import solve_captcha_with_openai

# Mapping from schema field names to dropdown text
STATE_MAPPING = {
    "Andaman_Nicobar_Islands": "Andaman & Nicobar Islands",
    "Andhra_Pradesh": "Andhra Pradesh",
    "Arunachal_Pradesh": "Arunachal Pradesh",
    "Assam": "Assam",
    "Bihar": "Bihar",
    "Chandigarh": "Chandigarh",
    "Chhattisgarh": "Chhattisgarh",
    "Dadra_Nagar_Haveli_Daman_Diu": "Dadra & Nagar Haveli and Daman & Diu",
    "Goa": "Goa",
    "Gujarat": "Gujarat",
    "Haryana": "Haryana",
    "Himachal_Pradesh": "Himachal Pradesh",
    "Jammu_and_Kashmir": "Jammu and Kashmir",
    "Jharkhand": "Jharkhand",
    "Karnataka": "Karnataka",
    "Kerala": "Kerala",
    "Ladakh": "Ladakh",
    "Lakshadweep": "Lakshadweep",
    "Madhya_Pradesh": "Madhya Pradesh",
    "Maharashtra": "Maharashtra",
    "Manipur": "Manipur",
    "Meghalaya": "Meghalaya",
    "Mizoram": "Mizoram",
    "Nagaland": "Nagaland",
    "NCT_OF_Delhi": "NCT OF Delhi",
    "Odisha": "Odisha",
    "Puducherry": "Puducherry",
    "Punjab": "Punjab",
    "Rajasthan": "Rajasthan",
    "Sikkim": "Sikkim",
    "Tamil_Nadu": "Tamil Nadu",
    "Telangana": "Telangana",
    "Tripura": "Tripura",
    "Uttar_Pradesh": "Uttar Pradesh",
    "Uttarakhand": "Uttarakhand",
    "West_Bengal": "West Bengal"
}

def verify_voter_id(driver, epic_number, state_flags, api_key, max_retries=3):
    wait = WebDriverWait(driver, 10)
    
    # Get the state marked as True
    selected_states = [key for key, enabled in state_flags.items() if enabled]
    
    if not selected_states:
        return {"success": False, "message": "No state selected. Set at least one state to true."}
    
    # Use the first selected state
    state_key = selected_states[0]
    state = STATE_MAPPING.get(state_key)
    
    if not state:
        return {"success": False, "message": f"Invalid state key: {state_key}"}
    
    print(f"====== Searching in state: {state} ======")

    for attempt in range(1, max_retries + 1):
        print(f"\n---->>>>>>  Attempt {attempt} of {max_retries}...")

        try:
            driver.get("https://electoralsearch.eci.gov.in/")
            time.sleep(5)

            refresh_voter_captcha(driver)
            base64_img = extract_voter_captcha_image(driver)

            question = """Extract text from the captcha image in english language. Maintain the case of the text. It contains numbers [0-9], alphabets [A-Z] or [a-z] and Dont Consider Space and total length of the text should be 6. """
            captcha_val = solve_captcha_with_openai(base64_img, question, api_key)

            epic_input = wait.until(EC.presence_of_element_located((By.ID, "epicID")))
            epic_input.clear()
            epic_input.send_keys(epic_number)

            state_dropdowns = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='library-select']/select")))
            second_state_dropdown = state_dropdowns[1]
            state_select = Select(second_state_dropdown)

            available_states = [option.text.strip() for option in state_select.options]
            if state in available_states:
                state_select.select_by_visible_text(state)
                print(f"Selected state: {state}")
            else:
                print(f"Error: '{state}' not found in dropdown.")
                return {"success": False, "message": f"State '{state}' not found in dropdown."}

            captcha_input = wait.until(EC.presence_of_element_located((By.NAME, "captcha")))
            captcha_input.clear()
            captcha_input.send_keys(captcha_val)

            # Click the search button via JS
            button_click_script = """
            const siblingButtons = Array.from(document.querySelectorAll('button.btn-active'));
            if (siblingButtons.length > 0) {
                siblingButtons[0].style.position = 'relative';
                siblingButtons[0].style.zIndex = '1';
                siblingButtons[0].click();
            }
            return siblingButtons.length;
            """
            button_count = driver.execute_script(button_click_script)

            print(f"Clicked {button_count} active button(s)." if button_count else "No active buttons found!")
            time.sleep(5)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            table = soup.find("table", class_="result-table")

            if table:
                response_data = {}

                name = soup.find("h2", class_="result-name")
                if name:
                    response_data["Name"] = name.get_text(strip=True)

                headers = [b.get_text(strip=True) for b in table.find("thead").find_all("b")]
                rows = []
                for row in table.find("tbody").find_all("tr"):
                    cells = row.find_all("td")
                    row_data = {headers[i]: cells[i].get_text(strip=True) for i in range(len(cells))}
                    rows.append(row_data)

                response_data["Details"] = rows

                # Only save if data is non-empty
                os.makedirs("data", exist_ok=True)
                json_filename = os.path.join("data", f"Voter_{epic_number}.json")
                with open(json_filename, "w", encoding="utf-8") as f:
                    json.dump(response_data, f, indent=4, ensure_ascii=False)

                print(f"Voter ID data saved to '{json_filename}'")
                
                return {
                    "success": True,
                    "epic_number": epic_number,
                    "response": response_data
                }

            else:
                print(" CAPTCHA might be wrong or no data found, retrying...")

        except Exception as e:
            print(f"Attempt {attempt} failed with error: {e}")

    print(" All attempts failed.")
    return {
        "success": False,
        "epic_number": epic_number,
        "message": "All attempts failed or no valid data found."
    }
