from fastapi import FastAPI, HTTPException, Request
import httpx
import redis
import json
import os

app = FastAPI(title="API Gateway")

# --- Configuration ---
# Internal Service URLs (Not exposed to outside world)
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://users:8000")
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://products:8000")
ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://orders:8000")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://payments:8000")

# Redis Cache
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

# --- Helper: Proxy Request ---
async def proxy_request(service_url: str, path: str, method: str, payload: dict = None):
    async with httpx.AsyncClient() as client:
        url = f"{service_url}{path}"
        try:
            if method == "GET":
                resp = await client.get(url)
            elif method == "POST":
                resp = await client.post(url, json=payload)
            else:
                raise HTTPException(status_code=405, detail="Method not supported in Gateway MVP")
            
            return resp.json(), resp.status_code
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Service Unavailable")

# --- Routes: Users ---
@app.post("/users")
async def create_user(request: Request):
    payload = await request.json()
    data, status = await proxy_request(USER_SERVICE_URL, "/users", "POST", payload)
    if status != 200:
        raise HTTPException(status_code=status, detail=data)
    return data

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    # TODO: Add Authentication Check Here
    data, status = await proxy_request(USER_SERVICE_URL, f"/users/{user_id}", "GET")
    if status != 200:
        raise HTTPException(status_code=status, detail=data)
    return data

# --- Routes: Products (WITH CACHING) ---
@app.get("/products")
async def list_products():
    # 1. Check Cache
    cache_key = "all_products"
    cached_data = redis_client.get(cache_key)
    if cached_data:
        print("Cache Hit! Returning data from Redis.")
        return json.loads(cached_data)
    
    # 2. Fetch from Service if not in cache
    print("Cache Miss. Fetching from Product Service...")
    data, status = await proxy_request(PRODUCT_SERVICE_URL, "/products", "GET")
    
    # 3. Save to Cache (Expire in 60 seconds)
    if status == 200:
        redis_client.setex(cache_key, 60, json.dumps(data))
    
    return data

@app.post("/products")
async def create_product(request: Request):
    payload = await request.json()
    data, status = await proxy_request(PRODUCT_SERVICE_URL, "/products", "POST", payload)
    
    # Invalidate Cache on Update
    redis_client.delete("all_products")
    
    return data

# --- Routes: Orders ---
@app.post("/orders")
async def create_order(request: Request):
    payload = await request.json()
    # Rate Limiting Logic could go here
    data, status = await proxy_request(ORDER_SERVICE_URL, "/orders", "POST", payload)
    if status != 200:
         raise HTTPException(status_code=status, detail=data)
    return data

@app.get("/")
def home():
    return {"message": "Welcome to E-Commerce Stage 4: API Gateway"}
