from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db, Customer
from backend.auth import get_current_user
from backend.models import MilesResponse

router = APIRouter()


@router.get("/", response_model=MilesResponse)
def get_miles(
    current_user: Customer = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return MilesResponse(
        name=current_user.name,
        tier=current_user.tier,
        miles_balance=current_user.miles_balance,
    )
