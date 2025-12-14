from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import List, Optional

app = FastAPI(title="E-Commerce Stage 2: Database Persistence")

# --- Database Setup ---
sqlite_file_name = "ecommerce.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# --- Models ---

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    price: float
    description: str

class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    status: str = "pending"
    total_price: float = 0.0

class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    product_id: int = Field(foreign_key="product.id")
    quantity: int

# --- Pydantic Schemas for Requests (to handle nested data) ---
from pydantic import BaseModel
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItemCreate]

# --- Lifecycle ---
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# --- Routes: Users ---
@app.post("/users", response_model=User)
def create_user(user: User, session: Session = Depends(get_session)):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@app.get("/users", response_model=List[User])
def list_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users

# --- Routes: Products ---
@app.post("/products", response_model=Product)
def create_product(product: Product, session: Session = Depends(get_session)):
    session.add(product)
    session.commit()
    session.refresh(product)
    return product

@app.get("/products", response_model=List[Product])
def list_products(session: Session = Depends(get_session)):
    products = session.exec(select(Product)).all()
    return products

# --- Routes: Orders ---
@app.post("/orders", response_model=Order)
def create_order(order_data: OrderCreate, session: Session = Depends(get_session)):
    # 1. Verify User
    user = session.get(User, order_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 2. Create Order Object
    order = Order(user_id=order_data.user_id, status="pending")
    session.add(order)
    session.commit()
    session.refresh(order)
    
    # 3. Process Items & Calculate Total
    total = 0.0
    for item_data in order_data.items:
        product = session.get(Product, item_data.product_id)
        if not product:
            # Rollback in a real app or handle error
            raise HTTPException(status_code=404, detail=f"Product {item_data.product_id} not found")
        
        # Check inventory here if we had it
        
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item_data.quantity
        )
        session.add(order_item)
        total += product.price * item_data.quantity
        
    order.total_price = total
    order.status = "confirmed"
    session.add(order)
    session.commit()
    session.refresh(order)
    return order

@app.get("/orders", response_model=List[Order])
def list_orders(session: Session = Depends(get_session)):
    orders = session.exec(select(Order)).all()
    return orders

@app.get("/")
def home():
    return {"message": "Welcome to E-Commerce Stage 2: Database Persistence (SQLite)"}
