# E-Commerce Evolution: From 1 to 1 Million Users

This project demonstrates the evolution of an e-commerce backend from a simple script to a complex, scalable microservices architecture. Each stage represents a branch in this repository.

## The Goal
Build a robust e-commerce platform with 4 core domains:
1.  **Users** (Auth, Profiles)
2.  **Products** (Catalog, Search)
3.  **Orders** (Cart, Checkout)
4.  **Payments** (Transactions, Inventory checks)

## Evolution Stages

### Stage 1: The MVP (1 User)
*   **Architecture**: Monolithic (Single Process).
*   **Database**: In-Memory Lists.
*   **Focus**: Core business logic, basic API endpoints.
*   **Tech**: Python (FastAPI), Local Storage.
*   **Branch**: `stage-1-mvp`
*   **Scenario**: Validating the idea. Simplicity is key.

```mermaid
graph LR
    User((User)) -->|HTTP Requests| API[FastAPI Monolith]
    API -->|Read/Write| Memory[(In-Memory Lists)]
    style API fill:#f9f,stroke:#333,stroke-width:2px
```

### Stage 2: The Startup (10-100 Users)
*   **Architecture**: Monolithic (Single Process).
*   **Database**: PostgreSQL (Client-Server Database).
*   **Focus**: Data persistence, schema structure, basic concurrency.
*   **Tech**: Docker for DB, SQLAlchemy ORM.
*   **Branch**: `stage-2-database`
*   **Scenario**: Small user base, need reliable data storage.

```mermaid
graph LR
    User((User)) -->|HTTP Requests| API[FastAPI Monolith]
    API -->|SQL| DB[(SQLite/Postgres)]
    style API fill:#f9f,stroke:#333,stroke-width:2px
    style DB fill:#bbf,stroke:#333,stroke-width:2px
```

### Stage 3: The Growth (100-1,000 Users) - Microservices Split
*   **Architecture**: Microservices (4 logical services).
*   **Database**: Separate Databases for each service (Database-per-Service pattern).
*   **Focus**: Placing boundaries, Docker Compose orchestration.
*   **Tech**: Docker Compose, 4 x FastAPI instances, Internal HTTP calls.
*   **Branch**: `stage-3-microservices`
*   **Scenario**: Different teams working on different features, need decoupling.

```mermaid
graph TD
    User((User)) -->|HTTP| Users[User Service]
    User -->|HTTP| Products[Product Service]
    User -->|HTTP| Orders[Order Service]
    
    %% Internal Service Communication
    Orders -->|HTTP Get User| Users
    Orders -->|HTTP Get Product| Products
    Orders -->|HTTP Process| Payments[Payment Service]
    
    %% Databases
    Users -->|SQL| UserDB[(User DB)]
    Products -->|SQL| ProdDB[(Product DB)]
    Orders -->|SQL| OrderDB[(Order DB)]
    Payments -->|SQL| PayDB[(Payment DB)]
    
    style Users fill:#f96,stroke:#333
    style Products fill:#96f,stroke:#333
    style Orders fill:#6f9,stroke:#333
    style Payments fill:#ff9,stroke:#333
```

### Stage 4: The Scale (10,000 Users) - Gateway & Caching
*   **Architecture**: Microservices with API Gateway.
*   **Infrastructure**: API Gateway, Redis Cache.
*   **Focus**: Rate Limiting, Response Caching, Centralized Authentication.
*   **Tech**: Nginx/Kong or Custom Gateway, Redis.
*   **Branch**: `stage-4-gateway`
*   **Scenario**: Traffic spikes, need to protect backend services.

```mermaid
graph TD
    User((User)) -->|HTTP| Gateway[API Gateway]
    
    Gateway -->|Check| Cache[(Redis Cache)]
    
    %% Gateway Routing
    Gateway -->|Route /users| Users[User Service]
    Gateway -->|Route /products| Products[Product Service]
    Gateway -->|Route /orders| Orders[Order Service]
    Gateway -->|Route /payments| Payments[Payment Service]
    
    %% Internal Auth Check
    Gateway -.->|Auth Token| Users
    
    style Gateway fill:#f9f,stroke:#333,stroke-width:4px
    style Cache fill:#f00,stroke:#333
```

### Stage 5: The Enterprise (1 Million+ Users) - Sharding & Async
*   **Architecture**: Event-Driven Microservices.
*   **Infrastructure**: Kafka/RabbitMQ, Database Sharding, Read Replicas.
*   **Focus**: High Availability, Eventual Consistency, Horizontal Scaling.
*   **Tech**: Message Queues, Horizontal Partitioning (Sharding).
*   **Branch**: `stage-5-enterprise`
*   **Scenario**: Global scale, massive transaction volume.

```mermaid
graph TD
    User((User)) -->|HTTP| Gateway[API Gateway]
    
    %% Sync Path
    Gateway -->|Read Query| ReadReplica[(Read Replica)]
    
    %% Async Path
    Gateway -->|Write Command| MQ{Kafka Message Queue}
    
    MQ -->|Event: OrderPlaced| OrderWorker[Order Worker]
    MQ -->|Event: PaymentProcessed| PaymentWorker[Payment Worker]
    MQ -->|Event: InventoryUpdate| InventoryWorker[Inventory Worker]
    
    OrderWorker -->|Write| MasterDB[(Sharded Master DB)]
    PaymentWorker -->|Write| PayDB[(Payment DB)]
    
    style MQ fill:#fc0,stroke:#333
    style OrderWorker fill:#6f9,stroke:#333
    style PaymentWorker fill:#ff9,stroke:#333
```

## How to use
Switch branches to see how the code evolves!
