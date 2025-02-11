from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class HealthResponse(BaseModel):
    """Response model for health check
    
    Attributes:
        status (str): Status of the health check
    """
    status: str

@router.get("", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok")
