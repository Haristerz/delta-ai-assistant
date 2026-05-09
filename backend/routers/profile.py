from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db, Customer
from backend.auth import get_current_user
from backend.models import ProfileResponse

router = APIRouter()


@router.get("/", response_model=ProfileResponse)
def get_profile(
    current_user: Customer = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ProfileResponse.model_validate(current_user)
