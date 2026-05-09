from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from passlib.context import CryptContext
import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.config import settings

# ── Engine & Session ──────────────────────────────────────────────────────────

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# ── Password Hashing ──────────────────────────────────────────────────────────

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── Tables ────────────────────────────────────────────────────────────────────

class Customer(Base):
    __tablename__ = "customers"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String, nullable=False)
    email         = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    tier          = Column(String, default="Silver")
    miles_balance = Column(Float, default=0.0)
    member_since  = Column(Date, default=datetime.date.today)

    activity = relationship("Activity", back_populates="customer")
    invoices = relationship("Invoice", back_populates="customer")


class Activity(Base):
    __tablename__ = "activity"

    id             = Column(Integer, primary_key=True, index=True)
    customer_id    = Column(Integer, ForeignKey("customers.id"), nullable=False)
    flight_number  = Column(String, nullable=False)
    origin         = Column(String, nullable=False)
    destination    = Column(String, nullable=False)
    flight_date    = Column(Date, nullable=False)
    miles_earned   = Column(Float, nullable=False)

    customer = relationship("Customer", back_populates="activity")


class Invoice(Base):
    __tablename__ = "invoices"

    id          = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    booking_ref = Column(String, nullable=False)
    route       = Column(String, nullable=False)
    amount      = Column(Float, nullable=False)
    invoice_date = Column(Date, nullable=False)
    status      = Column(String, default="Paid")

    customer = relationship("Customer", back_populates="invoices")

# ── Dependency: get DB session ────────────────────────────────────────────────

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ── Seed Data ─────────────────────────────────────────────────────────────────

def seed_data(db):
    if db.query(Customer).first():
        return

    customers = [
        Customer(
            name="Hariharan",
            email="hari@delta.com",
            password_hash=pwd_context.hash("hari123"),
            tier="Gold",
            miles_balance=45230.0,
            member_since=datetime.date(2019, 3, 15),
        ),
        Customer(
            name="Priya Sharma",
            email="priya@delta.com",
            password_hash=pwd_context.hash("priya123"),
            tier="Platinum",
            miles_balance=120500.0,
            member_since=datetime.date(2017, 7, 22),
        ),
        Customer(
            name="James Wilson",
            email="james@delta.com",
            password_hash=pwd_context.hash("james123"),
            tier="Silver",
            miles_balance=8750.0,
            member_since=datetime.date(2022, 1, 10),
        ),
    ]
    db.add_all(customers)
    db.commit()
    db.refresh(customers[0])
    db.refresh(customers[1])
    db.refresh(customers[2])

    activity_records = [
        Activity(customer_id=customers[0].id, flight_number="DL 204",  origin="JFK", destination="LAX", flight_date=datetime.date(2024, 11, 5),  miles_earned=2475.0),
        Activity(customer_id=customers[0].id, flight_number="DL 408",  origin="LAX", destination="ATL", flight_date=datetime.date(2024, 12, 18), miles_earned=1947.0),
        Activity(customer_id=customers[0].id, flight_number="DL 512",  origin="ATL", destination="ORD", flight_date=datetime.date(2025, 1, 30),  miles_earned=606.0),
        Activity(customer_id=customers[1].id, flight_number="DL 100",  origin="JFK", destination="LHR", flight_date=datetime.date(2024, 10, 12), miles_earned=3459.0),
        Activity(customer_id=customers[1].id, flight_number="DL 302",  origin="LHR", destination="CDG", flight_date=datetime.date(2024, 10, 14), miles_earned=215.0),
        Activity(customer_id=customers[2].id, flight_number="DL 720",  origin="BOS", destination="MIA", flight_date=datetime.date(2025, 2, 20),  miles_earned=1258.0),
    ]
    db.add_all(activity_records)

    invoices = [
        Invoice(customer_id=customers[0].id, booking_ref="BKDL1001", route="JFK → LAX", amount=389.50,  invoice_date=datetime.date(2024, 11, 5),  status="Paid"),
        Invoice(customer_id=customers[0].id, booking_ref="BKDL1002", route="LAX → ATL", amount=274.00,  invoice_date=datetime.date(2024, 12, 18), status="Paid"),
        Invoice(customer_id=customers[1].id, booking_ref="BKDL2001", route="JFK → LHR", amount=892.75,  invoice_date=datetime.date(2024, 10, 12), status="Paid"),
        Invoice(customer_id=customers[2].id, booking_ref="BKDL3001", route="BOS → MIA", amount=215.00,  invoice_date=datetime.date(2025, 2, 20),  status="Paid"),
    ]
    db.add_all(invoices)
    db.commit()


# ── Init ──────────────────────────────────────────────────────────────────────

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    print("Database created and seeded successfully.")
