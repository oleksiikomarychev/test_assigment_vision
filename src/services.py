from io import BytesIO
import google.generativeai as genai
import os
from PIL import Image
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)

gemini_api_key = os.getenv("GOOGLE_API_KEY")
if not gemini_api_key:
    raise ValueError("GOOGLE_API_KEY не установлен в файле .env")

genai.configure(api_key=gemini_api_key)

model_name = os.getenv("MODEL_NAME", "gemini-1.5-flash")
model = genai.GenerativeModel(model_name)


def query_gemini(image_data, question):
    try:
        if not isinstance(image_data, Image.Image):
            image_data = Image.open(BytesIO(image_data))

        response = model.generate_content(
            [
                "Ответить на вопрос",
                image_data,
                question
            ],
            stream=False
        )
        return response.text
    except Exception as e:
        logging.error(f"Ошибка вызова Gemini API: {e}")
        return None
