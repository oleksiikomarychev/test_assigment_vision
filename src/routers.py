import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File, Response, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src import models
from src.services import query_gemini_websocket, query_gemini_http
from src.image_utils import capture_image_stream, process_image, encode_image, decode_image
from typing import Annotated

image_router = APIRouter()
websocket_router = APIRouter()


@image_router.post("/query/")
async def create_query(
        question: str,
        image: Annotated[UploadFile, File()],
        db: Session = Depends(get_db)
):
    image_data = await image.read()
    processed_image = process_image(image_data)

    if processed_image is None:
        raise HTTPException(status_code=400, detail="Error processing image")
    response_text = await query_gemini_http(processed_image, question)
    if response_text is None:
        raise HTTPException(status_code=500, detail="Error getting response from Gemini")
    db_query_response = models.QueryResponse(
        question=question,
        image_data=image_data,
        response=response_text
    )
    db.add(db_query_response)
    db.commit()
    db.refresh(db_query_response)

    return {
        "id": db_query_response.id,
        "question": db_query_response.question,
        "image": encode_image(db_query_response.image_data),
        "response": db_query_response.response
    }

@image_router.get("/query/{query_id}")
async def get_query(query_id: int, db: Session = Depends(get_db)):
    db_query_response = db.get(models.QueryResponse, query_id)
    if db_query_response is None:
        raise HTTPException(status_code=404, detail="Query not found")
    return {
        "id": db_query_response.id,
        "question": db_query_response.question,
        "image": encode_image(db_query_response.image_data),
        "response": db_query_response.response
    }

@image_router.get("/image/{query_id}")
async def get_image(query_id: int, db: Session = Depends(get_db)):
    db_query_response = db.get(models.QueryResponse, query_id)
    if db_query_response is None:
        raise HTTPException(status_code=404, detail="Query not found")

    image_data = decode_image(db_query_response.image_data)
    return Response(content=image_data, media_type="image/jpeg")

@image_router.post("/capture/", response_class=Response)
async def capture_image(websocket: WebSocket = None):
    if websocket:
        image_data = await capture_image_stream(websocket)
        if image_data is None:
            raise HTTPException(status_code=500, detail="Ошибка при захвате изображения")
        return Response(content=image_data, media_type="image/jpeg")
    else:
        image_data = await capture_image_stream(None)
        if image_data is None:
            raise HTTPException(status_code=500, detail="Ошибка при захвате изображения")
        return Response(content=image_data, media_type="image/jpeg")

@websocket_router.websocket("/ws/query")
async def websocket_query(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            question = data.get("question")
            image_data = data.get("image")

            if not question or not image_data:
                await websocket.send_text("Вопрос или изображение отсутствуют.")
                continue

            await query_gemini_websocket(image_data, question, websocket)

    except WebSocketDisconnect:
        logging.info("Клиент отключился")

@websocket_router.websocket("/ws/capture")
async def websocket_capture(websocket: WebSocket):
    await websocket.accept()
    await capture_image_stream(websocket)