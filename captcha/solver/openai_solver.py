# captcha/solver/openai_solver.py

import base64
import io
import os
import tempfile
from openai import OpenAI

def solve_captcha_with_openai(image_input, question, api_key):
    file_to_cleanup = None
    
    # Check if input is a file path or base64 string
    if os.path.isfile(str(image_input)):
        # It's a file path
        file_to_cleanup = image_input
        with open(image_input, "rb") as image_file:
            image_bytes = image_file.read()
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
    else:
        # It's a base64 string
        base64_image = image_input
        # Pad base64 if needed
        base64_image = base64_image + '=' * (-len(base64_image) % 4)
    
    # Always use jpeg as mime type for compatibility
    mime_type = "image/jpeg"
    
    client = OpenAI(api_key=api_key)

    system_prompt = """You are a CAPTCHA text extraction expert. Your task is to accurately read and extract text from CAPTCHA images.

Rules:
- Return ONLY the exact characters you see in the image, nothing else
- Do not add any explanation, quotes, or extra text
- Maintain exact case sensitivity (uppercase/lowercase)
- Include numbers exactly as shown
- If characters are distorted, make your best guess
- Never return empty response - always attempt to read the text"""

    try:
        for attempt in range(3):
            print(f"Attempt {attempt + 1} of 3...")
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": f"{question}\n\nIMPORTANT: Return ONLY the captcha text, no quotes or explanation."},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{mime_type};base64,{base64_image}",
                                        "detail": "high"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=50,
                    temperature=0
                )
                captcha_text = response.choices[0].message.content.strip()
                # Clean up any quotes or extra characters
                captcha_text = captcha_text.strip('"\'` ')
                print(f"CAPTCHA Solved: {captcha_text}")
                return captcha_text
            except Exception as e:
                print(f"Attempt {attempt + 1} failed with error: {e}")
        
        print("All attempts failed.")
        return None
    finally:
        # Cleanup temp file
        if file_to_cleanup and os.path.exists(file_to_cleanup):
            try:
                os.remove(file_to_cleanup)
                print(f"Temp captcha image deleted: {file_to_cleanup}")
            except:
                pass
