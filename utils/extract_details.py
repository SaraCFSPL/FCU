import re

def extract_gvcl_details_from_text(ocr_text):
    result = {}
    ocr_text = re.sub(r"\s+", " ", ocr_text.strip())

    fields = {
        "Consumer Name": r"Consumer Name\s+([A-Z\s]+)",
        "CONSUMER NO": r"CONSUMER NO\.*\s+(\d{5,15})",
        "Last Paid Detail": r"Last Paid Detail\s+(Rs\.\d+\.?\d*\s+paid\s+on\s+\d{4}-\d{2}-\d{2}.*?)\s+(?=\w)",
        "Outstanding Amount": r"Outstanding Amount\(Tentative\)\s+(\d+)",
        "Bill Date": r"Bill Date\s+(\d{4}-\d{2}-\d{2})",
        "Amount to Pay": r"Amount to Pay\*\s+(\d+)",
        "E-mail": r"E-mail \(optional\)\s+([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)",
        "Mobile No": r"Mobile No\s+(Enter 10 Digit Mobile Number|\d{10})"
    }

    for key, pattern in fields.items():
        match = re.search(pattern, ocr_text)
        if match:
            result[key] = match.group(1).strip()
        else:
            result[key] = None

    return result
