import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)

gemini_api_key = os.getenv("GOOGLE_API_KEY")
if not gemini_api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set.")

genai.configure(api_key=gemini_api_key)

model_name = os.getenv("MODEL_NAME", "gemini-1.5-flash")
model = genai.GenerativeModel(model_name)


def query_gemini(image_data, question):
    """Sends a query to the Gemini API."""
    try:
        response = model.generate_content(
            [
                "You are a helpful assistant that can see images and answer questions about them.",
                image_data,
                question
            ],
            stream=False
        )
        return response.text
    except Exception as e:
        logging.error(f"Error querying Gemini API: {e}")
        return None
