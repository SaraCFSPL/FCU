# util/solve.py

import base64
from langchain.schema import HumanMessage
from langchain_openai import ChatOpenAI

def solve_captcha_with_openai(base64_image, question, api_key):
    model = ChatOpenAI(
        model="gpt-4o",
        api_key=api_key
    )

    message = HumanMessage(content=[
        {"type": "text", "text": question},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
    ])

    return model.invoke([message]).content.strip()
