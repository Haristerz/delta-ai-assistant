from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db, Customer
from backend.auth import get_current_user
from backend.models import ChatRequest, ChatResponse
from ai_engine.llm_client import get_ai_response

router = APIRouter()


@router.post("/", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    current_user: Customer = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    customer_context = {
        "name":          current_user.name,
        "tier":          current_user.tier,
        "miles_balance": current_user.miles_balance,
        "member_since":  str(current_user.member_since),
    }

    result = get_ai_response(request.message, customer_context)

    return ChatResponse(
        reply=result["reply"],
        intent=result["intent"],
        used_rag=result["used_rag"],
    )
