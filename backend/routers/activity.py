from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db, Customer, Activity
from backend.auth import get_current_user
from backend.models import ActivityResponse, ActivityItem

router = APIRouter()


@router.get("/", response_model=ActivityResponse)
def get_activity(
    current_user: Customer = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records = (
        db.query(Activity)
        .filter(Activity.customer_id == current_user.id)
        .order_by(Activity.flight_date.desc())
        .all()
    )

    return ActivityResponse(
        name=current_user.name,
        total_flights=len(records),
        activity=[ActivityItem.model_validate(r) for r in records],
    )
