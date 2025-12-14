from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid

app = FastAPI(title="E-Commerce Stage 1: MVP (In-Memory)")

# --- In-Memory Database ---
users_db = []
products_db = []
orders_db = []

# --- Models ---
class User(BaseModel):
    id: Optional[str] = None
    username: str
    email: str

class Product(BaseModel):
    id: Optional[str] = None
    name: str
    price: float
    description: str

class OrderItem(BaseModel):
    product_id: str
    quantity: int

class Order(BaseModel):
    id: Optional[str] = None
    user_id: str
    items: List[OrderItem]
    total_price: float = 0.0
    status: str = "pending"

# --- Routes: Users ---
@app.post("/users", response_model=User)
def create_user(user: User):
    user.id = str(uuid.uuid4())
    users_db.append(user)
    return user

@app.get("/users", response_model=List[User])
def list_users():
    return users_db

# --- Routes: Products ---
@app.post("/products", response_model=Product)
def create_product(product: Product):
    product.id = str(uuid.uuid4())
    products_db.append(product)
    return product

@app.get("/products", response_model=List[Product])
def list_products():
    return products_db

# --- Routes: Orders ---
@app.post("/orders", response_model=Order)
def create_order(order: Order):
    # Verify User
    user = next((u for u in users_db if u.id == order.user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Calculate Total & Verify Products
    total = 0.0
    for item in order.items:
        product = next((p for p in products_db if p.id == item.product_id), None)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        total += product.price * item.quantity
    
    order.id = str(uuid.uuid4())
    order.total_price = total
    order.status = "confirmed"
    orders_db.append(order)
    return order

@app.get("/orders", response_model=List[Order])
def list_orders():
    return orders_db

@app.get("/")
def home():
    return {"message": "Welcome to E-Commerce Stage 1: The Monolith MVP"}
