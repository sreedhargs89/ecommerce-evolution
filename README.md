# Stage 2: The Startup (Database)

We have evolved from in-memory lists to a persistent Relational Database (SQLite).
*   **Architecture**: Monolith (Single file) with DB.
*   **Database**: SQLite (File-based, persistent).
*   **Scale**: 10-100 Users (Small Business).

## Changes from Stage 1
*   Introduced `SQLModel` (ORM) for database interactions.
*   Defined Tables: `User`, `Product`, `Order`, `OrderItem`.
*   Data persists after server restart in `ecommerce.db`.

## How to Run

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2.  Run the server:
    ```bash
    uvicorn main:app --reload
    ```
    *The database file `ecommerce.db` will be created automatically.*

3.  Open Swagger UI:
    `http://127.0.0.1:8000/docs`

## Data Modeling
We now have relationships:
*   Orders belong to Users.
*   Orders have many Items (linked to Products).
