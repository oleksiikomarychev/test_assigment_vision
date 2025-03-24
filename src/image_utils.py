import time
import cv2
from PIL import Image
from io import BytesIO
import base64
import logging

logging.basicConfig(level=logging.INFO)


def process_image(image_data):
    try:
        image = Image.open(BytesIO(image_data))
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        return buffered.getvalue()
    except Exception as e:
        logging.error(f"Ошибка обработки изображения: {e}")
        return None

def encode_image(image_data):
    if isinstance(image_data, str):
        return image_data
    return base64.b64encode(image_data).decode("utf-8")

def decode_image(base64_image):
    if isinstance(base64_image, bytes):
        return base64_image
    return base64.b64decode(base64_image)

def capture_image_from_camera():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logging.error("Не удалось открыть камеру")
        return None

    try:
        time.sleep(2)
        ret, frame = cap.read()
        if not ret:
            logging.error("Не удалось прочитать кадр с камеры")
            return None
    finally:
        cap.release()

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)

    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    return buffered.getvalue()