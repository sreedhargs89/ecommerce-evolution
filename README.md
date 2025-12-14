# Stage 3: The Growth (Microservices)

We have split the monolith into 4 distinct microservices.
*   **Architecture**: Microservices (Managed by Docker Compose).
*   **communication**: HTTP (REST) via `httpx`.
*   **Database**: Database-per-service (4 separate SQLite files).
*   **Scale**: 100-1,000 Users.

## Architecture
See `MASTER_PLAN.md` for the diagram.
1.  **Users Service** (Port 8001): Manages user profiles.
2.  **Products Service** (Port 8002): Manages catalog.
3.  **Orders Service** (Port 8003): Orchestrator. Calls Users, Products, and Payments.
4.  **Payments Service** (Port 8004): Handle transactions.

## How to Run

1.  **Start the Cluster**:
    ```bash
    docker-compose up --build
    ```

2.  **Test the Flow**:
    *   **Create User**:
        `POST http://localhost:8001/users` -> `{"username": "alice", "email": "alice@example.com"}`
    *   **Create Product**:
        `POST http://localhost:8002/products` -> `{"name": "Laptop", "price": 1000, "description": "Fast"}`
    *   **Place Order** (The Magic Happens Here):
        `POST http://localhost:8003/orders` -> `{"user_id": 1, "product_id": 1, "quantity": 1}`

    *Watch the `orders` service logs to see it calling the other services!*

## Key Changes from Stage 2
*   **Decoupling**: Services can't access each other's database. They MUST use the API.
*   **Orchestration**: `docker-compose` manages the lifecycle and network.
*   **Fault Isolation**: If `products` service crashes, `users` service still works (though orders will fail).
