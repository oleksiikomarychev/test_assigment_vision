from sqlalchemy import Column, Integer, String, LargeBinary
from src.database import Base


class QueryResponse(Base):
    __tablename__ = "query_responses"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, nullable=False)
    image_data = Column(LargeBinary, nullable=False)
    response = Column(String, nullable=False)
