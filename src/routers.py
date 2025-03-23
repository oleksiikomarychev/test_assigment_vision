from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response
from sqlalchemy.orm import Session
from src.database import get_db
from src import models
from src.services import query_gemini
from src.image_utils import process_image, encode_image, decode_image, capture_image_from_camera
from typing import Annotated, Any

router = APIRouter()


@router.post("/query/")
async def create_query(
        question: str,
        image: Annotated[UploadFile, File()],
        db: Session = Depends(get_db)
):
    """
    Endpoint to send a question and an image to the Gemini API.
    """
    image_data = await image.read()
    processed_image = process_image(image_data)

    if processed_image is None:
        raise HTTPException(status_code=400, detail="Error processing image")

    response_text = query_gemini(processed_image, question)

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


@router.get("/query/{query_id}")
async def get_query(query_id: int, db: Session = Depends(get_db)):
    """
    Endpoint to get a query and its response by ID.
    """
    db_query_response = db.query(models.QueryResponse).filter(models.QueryResponse.id == query_id).first()
    if db_query_response is None:
        raise HTTPException(status_code=404, detail="Query not found")
    return {
        "id": db_query_response.id,
        "question": db_query_response.question,
        "image": encode_image(db_query_response.image_data),
        "response": db_query_response.response
    }


@router.get("/image/{query_id}")
async def get_image(query_id: int, db: Session = Depends(get_db)):
    """
    Endpoint to get an image by query ID.
    """
    db_query_response = db.query(models.QueryResponse).filter(models.QueryResponse.id == query_id).first()
    if db_query_response is None:
        raise HTTPException(status_code=404, detail="Query not found")

    image_data = decode_image(db_query_response.image_data)
    return Response(content=image_data, media_type="image/jpeg")

@router.post("/capture/", response_class=Response)
async def capture_image():
    """API для захвата изображения с камеры."""
    image_data = capture_image_from_camera()
    if image_data is None:
        raise HTTPException(status_code=500, detail="Ошибка при захвате изображения")

    return Response(content=image_data, media_type="image/jpeg")