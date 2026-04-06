# utils/select_company.py

from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def select_company(driver, company_code):
    try:
        wait = WebDriverWait(driver, 10)
        wait = WebDriverWait(driver, 10)
        dropdown_element = wait.until(EC.presence_of_element_located((By.ID, "companyname")))
        company_select = Select(dropdown_element)
        available_companies = [option.text.strip() for option in company_select.options]

        if company_code in available_companies:
            company_select.select_by_visible_text(company_code)
            print(f" Selected company: {company_code}")
        else:
            print(f" Error: '{company_code}' not found. Available: {available_companies}")
    except Exception as e:
        print(f"Error selecting company: {e}")