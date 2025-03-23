import time
import cv2
from PIL import Image, UnidentifiedImageError
from io import BytesIO
import base64
import logging
from src.services import query_gemini  # Import query_gemini

logging.basicConfig(level=logging.INFO)


def process_image(image_data):
    """Форматирует изображение в структуру, совместимую с Gemini API."""
    try:
        from base64 import b64encode
        from io import BytesIO
        from PIL import Image

        # Открываем изображение и конвертируем в байты
        image = Image.open(BytesIO(image_data))
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        encoded_image = b64encode(buffered.getvalue()).decode("utf-8")

        return {
            "parts": [
                {
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": encoded_image
                    }
                }
            ]
        }

    except Exception as e:
        print(f"Ошибка обработки изображения: {e}")
        return None

def encode_image(image_data):
    """Encodes image data to base64."""
    return base64.b64encode(image_data).decode("utf-8")


def decode_image(base64_image):
    """Decodes base64 image data."""
    return base64.b64decode(base64_image)


def capture_image_from_camera():
    """Функция для захвата изображения с камеры с разогревом."""
    cap = cv2.VideoCapture(0)  # 0 обычно представляет дефолтную камеру
    if not cap.isOpened():
        print("Ошибка: не удалось открыть камеру.")
        return None

    # Разогрев камеры (ждем несколько секунд, чтобы камера стабилизировалась)
    time.sleep(2)  # Подожди 2 секунды

    ret, frame = cap.read()
    if not ret:
        print("Ошибка: не удалось прочитать кадр с камеры.")
        cap.release()
        return None

    cap.release()
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Конвертируем в RGB
    img = Image.fromarray(frame_rgb)  # Преобразуем в объект PIL Image

    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    img_bytes = buffered.getvalue()
    return img_bytes