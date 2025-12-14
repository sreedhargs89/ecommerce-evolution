from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import List, Optional
import httpx

app = FastAPI(title="Order Service")

# --- Database ---
sqlite_file_name = "orders.db"
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

# --- External Service URLs (Docker DNS) ---
USER_SERVICE_URL = "http://users:8000"
PRODUCT_SERVICE_URL = "http://products:8000"
PAYMENT_SERVICE_URL = "http://payments:8000"

# --- Models ---
class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    product_id: int
    quantity: int
    total_price: float
    status: str = "pending"

class OrderCreate(SQLModel):
    user_id: int
    product_id: int
    quantity: int

# --- Helper: Call Payment Service ---
async def process_payment(order_id: int, amount: float):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{PAYMENT_SERVICE_URL}/payments", json={"order_id": order_id, "amount": amount})
            response.raise_for_status()
            print(f"Payment processed for Order {order_id}")
        except Exception as e:
            print(f"Payment failed for Order {order_id}: {e}")

# --- Routes ---
@app.post("/orders", response_model=Order)
async def create_order(order_data: OrderCreate, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    # 1. Validate User (Synch HTTP)
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(f"{USER_SERVICE_URL}/users/{order_data.user_id}")
            if res.status_code != 200:
                raise HTTPException(status_code=404, detail="User not found (Microservice Call)")
        except httpx.RequestError:
             raise HTTPException(status_code=503, detail="User service unavailable")

    # 2. Get Product Price (Synch HTTP)
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(f"{PRODUCT_SERVICE_URL}/products/{order_data.product_id}")
            if res.status_code != 200:
                raise HTTPException(status_code=404, detail="Product not found (Microservice Call)")
            product = res.json()
        except httpx.RequestError:
             raise HTTPException(status_code=503, detail="Product service unavailable")

    # 3. Create Order
    total_price = product['price'] * order_data.quantity
    order = Order(
        user_id=order_data.user_id,
        product_id=order_data.product_id,
        quantity=order_data.quantity,
        total_price=total_price,
        status="pending"
    )
    session.add(order)
    session.commit()
    session.refresh(order)

    # 4. Trigger Payment (Async Call)
    # background_tasks.add_task(process_payment, order.id, total_price)
    # For Stage 3, let's keep it synchronous to see the flow clearly
    await process_payment(order.id, total_price)
    
    order.status = "confirmed"
    session.add(order)
    session.commit()
    session.refresh(order)
    
    return order

@app.get("/orders", response_model=List[Order])
def list_orders(session: Session = Depends(get_session)):
    return session.exec(select(Order)).all()
