from openai import OpenAI

def solve_text_captcha_with_openai(raw_text, question, api_key):
    client = OpenAI(api_key=api_key)
    
    system_prompt = """You are a CAPTCHA solver expert. Your task is to solve math expressions or extract clean text from noisy CAPTCHA text.

Rules:
- If given a math expression, calculate and return ONLY the numeric result
- If given text, return ONLY the cleaned characters
- Do not add any explanation, quotes, or extra text
- Return just the answer, nothing else"""

    for attempt in range(1, 4):
        print(f"[OpenAI] Attempt {attempt} of 3...")
        try:
            prompt = f"{question}\n\nCAPTCHA text: {raw_text}\n\nReturn ONLY the answer, no explanation."
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=20,
                temperature=0
            )
            result = response.choices[0].message.content.strip()
            # Clean up any quotes or extra characters
            result = result.strip('"\'` ')
            print(f"[OpenAI] Solved CAPTCHA: {result}")
            return {
                "success": True,
                "captcha_text": result
            }
        except Exception as e:
            print(f"[OpenAI] Attempt {attempt} failed: {e}")
            last_error = str(e)

    print("[OpenAI] All attempts failed.")
    return {
        "success": False,
        "error": last_error if 'last_error' in locals() else "Unknown error"
    }
