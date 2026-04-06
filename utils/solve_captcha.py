import pytesseract
from PIL import Image

# For macOS, this is typically the path when installed via Homebrew
pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

def solve_tesseract_captcha(image_path: str) -> str:
    text = pytesseract.image_to_string(Image.open(image_path), config='--psm 7')
    captcha_extract = ''.join(text.strip().split())[:6]
    print("Extracted CAPTCHA:", captcha_extract)
    return captcha_extract
