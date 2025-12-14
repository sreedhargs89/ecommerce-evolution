from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import List, Optional

app = FastAPI(title="Payment Service")

# --- Database ---
sqlite_file_name = "payments.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# --- Models ---
class Payment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int
    amount: float
    status: str = "success"

class PaymentCreate(SQLModel):
    order_id: int
    amount: float

# --- Routes ---
@app.post("/payments", response_model=Payment)
def process_payment(payment_data: PaymentCreate, session: Session = Depends(get_session)):
    # Simulating payment processing
    payment = Payment(
        order_id=payment_data.order_id,
        amount=payment_data.amount,
        status="success"
    )
    session.add(payment)
    session.commit()
    session.refresh(payment)
    print(f"Processed payment for Order {payment.order_id}: ${payment.amount}")
    return payment

@app.get("/payments", response_model=List[Payment])
def list_payments(session: Session = Depends(get_session)):
    return session.exec(select(Payment)).all()
