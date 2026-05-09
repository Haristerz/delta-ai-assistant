from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db, Customer, Invoice
from backend.auth import get_current_user
from backend.models import InvoiceResponse, InvoiceItem

router = APIRouter()


@router.get("/", response_model=InvoiceResponse)
def get_invoices(
    current_user: Customer = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records = (
        db.query(Invoice)
        .filter(Invoice.customer_id == current_user.id)
        .order_by(Invoice.invoice_date.desc())
        .all()
    )

    return InvoiceResponse(
        name=current_user.name,
        total_invoices=len(records),
        invoices=[InvoiceItem.model_validate(r) for r in records],
    )
