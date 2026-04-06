import base64
from io import BytesIO
import time
import os
import tempfile
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from PIL import Image

logger = logging.getLogger(__name__)


VALID_FORMATS = ["jpg", "jpeg", "png", "webp", "bmp"]

def _save_captcha_image(base64_src, file_format="jpg"):
    file_format = file_format.lower()
    if file_format not in VALID_FORMATS:
        raise ValueError(f"Unsupported file format '{file_format}'. Supported formats: {', '.join(VALID_FORMATS)}")

    padded_base64 = base64_src + '=' * (-len(base64_src) % 4)
    image_data = base64.b64decode(padded_base64)

    image = Image.open(BytesIO(image_data))

    # Save to temp file
    suffix = f".{file_format}"
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    file_path = temp_file.name
    temp_file.close()
    
    # PIL expects "JPEG" not "JPG"
    pil_format = "JPEG" if file_format.lower() in ["jpg", "jpeg"] else file_format.upper()
    image.save(file_path, format=pil_format)

    print(f"CAPTCHA image saved (temp): {file_path}")
    return file_path

def save_base64_image(base64_data, file_format="png"):
    """Save base64 image data to a temp file"""
    image_data = base64.b64decode(base64_data)
    image = Image.open(BytesIO(image_data))
    
    suffix = f".{file_format}"
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    file_path = temp_file.name
    temp_file.close()
    
    pil_format = "JPEG" if file_format.lower() in ["jpg", "jpeg"] else file_format.upper()
    image.save(file_path, format=pil_format)
    
    print(f"CAPTCHA image saved (temp): {file_path}")
    return file_path
# ---------------- Aadhaar ----------------
def refresh_aadhar_captcha(driver, timeout=10):
    wait = WebDriverWait(driver, timeout)
    refresh_button = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "div.auth-form__captcha svg[data-testid='AutorenewIcon']")))
    refresh_button.click()
    time.sleep(2)

def extract_aadhar_captcha_image(driver, timeout=10):
    """
    Extract the Aadhaar CAPTCHA image from the page.
    The image will be saved in the format detected from the image itself.
    """
    wait = WebDriverWait(driver, timeout)
    captcha_img = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, ".auth-form__captcha-box img.auth-form__captcha-image")))
    src = captcha_img.get_attribute("src")
    
    if "," not in src:
        raise ValueError("Invalid CAPTCHA image src (not base64).")
    
    base64_src = src.split(",")[1]
    return _save_captcha_image(base64_src)


# ---------------- Voter ----------------
def refresh_voter_captcha(driver, timeout=10):
    wait = WebDriverWait(driver, timeout)
    refresh_buttons = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "img[alt='']")))
    if len(refresh_buttons) > 1:
        refresh_buttons[1].click()
    else:
        refresh_buttons[0].click()
    time.sleep(2)

def extract_voter_captcha_image(driver, timeout=10):
    wait = WebDriverWait(driver, timeout)
    captcha_img = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".captcha-div img")))
    src = captcha_img.get_attribute("src")

    if "," not in src:
        raise ValueError("Invalid CAPTCHA image src (not base64).")

    base64_src = src.split(",")[1]
    return _save_captcha_image(base64_src)

# ---------------- APEPDCL ----------------
def refresh_apepdcl_captcha(driver, timeout=10):
    wait = WebDriverWait(driver, timeout)
    refresh_button = wait.until(EC.element_to_be_clickable((By.ID, "Billreset")))
    refresh_button.click()
    time.sleep(2)

def extract_apepdcl_captcha(driver, timeout=10):
    wait = WebDriverWait(driver, timeout)
    wait.until(EC.presence_of_element_located((By.ID, "captchaCanvas")))
    
    base64_src = driver.execute_script("""
        var canvas = document.getElementById("captchaCanvas");
        return canvas.toDataURL("image/png").split(",")[1];
    """)
    if not base64_src:
        raise ValueError("Failed to extract CAPTCHA from canvas.")
    
    # Save to temp file
    return save_base64_image(base64_src, "png")

# --------------- DVVNL ----------------
def refresh_dvvnl_captcha(driver, timeout=10):
    wait = WebDriverWait(driver, timeout)
    refresh_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//img[contains(@onclick, 'refreshImage()')]"))
    )
    refresh_button.click()
    time.sleep(2)


def extract_dvvnl_captcha_image(driver, timeout=10):
    wait = WebDriverWait(driver, timeout)
    captcha_img = wait.until(EC.presence_of_element_located((By.ID, "refImage")))
    driver.execute_script("arguments[0].scrollIntoView();", captcha_img)

    # JavaScript to extract image as Base64
    canvas_script = """
        var img = document.getElementById('refImage');
        var canvas = document.createElement('canvas');
        canvas.width = img.width;
        canvas.height = img.height;
        var ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0);
        return canvas.toDataURL('image/png').split(',')[1];
    """
    image_base64 = driver.execute_script(canvas_script)

    image_path = _save_captcha_image(image_base64)
    
    return image_path 


#----------------Maharashtra----------------
def refresh_maha_captcha(driver, timeout=10):
    wait = WebDriverWait(driver, timeout)
    refresh_buttons = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "img[alt='refresh']")))
    if len(refresh_buttons) > 1:
        refresh_buttons[1].click()
    else:
        refresh_buttons[0].click()
    time.sleep(2)

def extract_maha_captcha_image(driver, timeout=10):
    wait = WebDriverWait(driver, timeout)
    canvas = wait.until(EC.presence_of_element_located((By.ID, "captcha")))
    base64_png = driver.execute_script("""
        var canvas = arguments[0];
        return canvas.toDataURL('image/png').substring(22);
    """, canvas)

    # Save to temp file
    return save_base64_image(base64_png, "png")

#----------------PUVNL----------------
def refresh_puvnl_captcha(driver):
    wait = WebDriverWait(driver, 10)
    refresh_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@onclick, 'createCaptcha')]")))
    refresh_button.click()

def extract_puvnl_captcha_image(driver, save_path="captcha.png"):
    time.sleep(2)
    canvas_base64 = driver.execute_script("""
        var canvas = document.querySelector('canvas#captcha');
        return canvas.toDataURL('image/png').split(',')[1];
    """)
    image_data = base64.b64decode(canvas_base64)
    with open(save_path, "wb") as f:
        f.write(image_data)
    return save_path    

#----------------Becom----------------

def refresh_bescom_captcha(driver):
    wait = WebDriverWait(driver, 10)
    refresh_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//mat-icon[normalize-space()='loop']")))
    refresh_button.click()

def extract_bescom_captcha_image(driver, save_path="captcha.png"):
    time.sleep(2)
    canvas_base64 = driver.execute_script("""
        var canvas = document.querySelector('canvas#captcha');
        return canvas.toDataURL('image/png').split(',')[1];
    """)
    image_data = base64.b64decode(canvas_base64)
    with open(save_path, "wb") as f:
        f.write(image_data)
    return save_path


#----------------Upcl----------------
def refresh_upcl_captcha(driver):
    """
    Clicks the 'Reload Image' link to refresh the UPCL CAPTCHA.
    """
    wait = WebDriverWait(driver, 10)
    refresh_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Reload Image')]"))
    )
    refresh_button.click()
    print("🔄 UPCL CAPTCHA refreshed.")

def extract_upcl_captcha_image(driver, save_path="captcha.png"):
    """
    Extracts the CAPTCHA image from the UPCL canvas element and saves it to a file.
    """
    time.sleep(2)  # Wait for canvas to refresh
    canvas_base64 = driver.execute_script("""
        var canvas = document.querySelector('canvas#captcha');
        return canvas.toDataURL('image/png').split(',')[1];
    """)
    image_data = base64.b64decode(canvas_base64)
    with open(save_path, "wb") as f:
        f.write(image_data)
    return save_path   


#----------------GVCL----------------
def extract_GVCL_captcha_image(driver):
    try:
        wait = WebDriverWait(driver, 20)
        captcha_img_element = wait.until(EC.presence_of_element_located((By.ID, "captcha")))
        driver.execute_script("arguments[0].scrollIntoView();", captcha_img_element)
        time.sleep(4)
        png_data = captcha_img_element.screenshot_as_png
        encoded_image = base64.b64encode(png_data).decode("utf-8")
        saved_image_path = save_base64_image(encoded_image)
        return saved_image_path
    except Exception as e:
        print(f"Error extracting CAPTCHA image: {e}")
        return None

#----------------TNPDCL----------------
def refresh_tnpdcl_captcha(driver):
    wait = WebDriverWait(driver, 10)
    refresh_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Refresh')]"))
    )
    refresh_button.click()
    time.sleep(2)


def extract_tnpdcl_captcha_image(driver):
    wait = WebDriverWait(driver, 10)
    time.sleep(2)  
    captcha_img = wait.until(EC.presence_of_element_located((By.ID, "CaptchaImgID")))
    captcha_base64 = captcha_img.screenshot_as_base64
    return _save_captcha_image(captcha_base64)

#----------------TPDDLL----------------
def extract_and_save_tpddl_captcha(driver):
    wait = WebDriverWait(driver, 10)
    captcha_img = wait.until(EC.presence_of_element_located((By.ID, "Img")))
    captcha_base64 = captcha_img.screenshot_as_base64
    return _save_captcha_image(captcha_base64)
   
#----------------UHBVN----------------
def extract_uhbvn_captcha(driver):
    wait = WebDriverWait(driver, 10)
    captcha_element = wait.until(EC.presence_of_element_located((By.ID, "code")))
    return captcha_element.text.strip()   

#----------------Stamp_Duty----------------
def extract_stamp_duty_captcha(driver):
    wait = WebDriverWait(driver, 10)
    time.sleep(2)  
    captcha_img = wait.until(EC.presence_of_element_located((By.ID, "cap")))
    captcha_base64 = captcha_img.screenshot_as_base64
    return _save_captcha_image(captcha_base64)

