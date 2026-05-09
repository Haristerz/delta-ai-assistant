from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date


# ── Auth ──────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── Customer Profile ──────────────────────────────────────────────────────────

class ProfileResponse(BaseModel):
    id: int
    name: str
    email: str
    tier: str
    miles_balance: float
    member_since: date

    class Config:
        from_attributes = True


# ── Miles ─────────────────────────────────────────────────────────────────────

class MilesResponse(BaseModel):
    name: str
    tier: str
    miles_balance: float

    class Config:
        from_attributes = True


# ── Activity ──────────────────────────────────────────────────────────────────

class ActivityItem(BaseModel):
    flight_number: str
    origin: str
    destination: str
    flight_date: date
    miles_earned: float

    class Config:
        from_attributes = True


class ActivityResponse(BaseModel):
    name: str
    total_flights: int
    activity: List[ActivityItem]


# ── Invoice ───────────────────────────────────────────────────────────────────

class InvoiceItem(BaseModel):
    booking_ref: str
    route: str
    amount: float
    invoice_date: date
    status: str

    class Config:
        from_attributes = True


class InvoiceResponse(BaseModel):
    name: str
    total_invoices: int
    invoices: List[InvoiceItem]


# ── Chat (AI Engine) ──────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    intent: Optional[str] = None
    used_rag: Optional[bool] = None
