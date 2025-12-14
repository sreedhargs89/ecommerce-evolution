# Stage 1: The MVP (Monolith)

This is the simplest possible version of our e-commerce app.
*   **Architecture**: Monolith (Single file)
*   **Database**: In-Memory (Python Lists)
*   **Scale**: 1 User (Proof of Concept)

## How to Run

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2.  Run the server:
    ```bash
    uvicorn main:app --reload
    ```

3.  Open Swagger UI:
    Visit `http://127.0.0.1:8000/docs` to interact with the API.

## Features
*   Create Users
*   Add Products
*   Place Orders

## Limitations
*   Data is lost when server restarts (In-Memory).
*   No concurrency handling.
*   No input validation beyond basic types.
