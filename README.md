# Cloud-Based Inventory Management System

A REST API for managing products, inventory, customers, and orders — built with FastAPI and SQLAlchemy, designed for cloud deployment on Microsoft Azure.

## Overview

This project simulates a real-world inventory management backend. It handles product catalog management, stock tracking across locations, customer records, and order processing — including stock validation and automatic inventory deduction when an order is placed.

## Tech Stack

- **Language:** Python
- **Framework:** FastAPI
- **Database:** SQLite (local development) — designed to be swapped for Azure SQL / PostgreSQL in production
- **ORM:** SQLAlchemy
- **Validation:** Pydantic
- **Server:** Uvicorn
- **Cloud:** Microsoft Azure (App Service)

## Features

- Full CRUD for Products, Inventory, Customers, and Orders
- Relational data model with foreign keys (Inventory → Product, Order → Customer, OrderItem → Order & Product)
- Order placement logic that validates stock availability and atomically deducts inventory across locations
- Auto-generated interactive API documentation (Swagger UI)
- Clean separation of concerns: database config, models, schemas, and route logic

## Data Model

```
Customer ──< Order ──< OrderItem >── Product ──< Inventory
```

- **Product** — catalog item (name, SKU, description, price)
- **Inventory** — stock quantity for a product at a given location
- **Customer** — customer contact details
- **Order** — a customer's order, with a status (pending/completed/cancelled)
- **OrderItem** — join table linking an Order to the Products (and quantities) it contains

## API Endpoints

| Resource | Endpoints |
|---|---|
| Products | `GET /products`, `GET /products/{id}`, `POST /products`, `PUT /products/{id}`, `DELETE /products/{id}` |
| Inventory | `GET /inventory`, `GET /inventory/{id}`, `POST /inventory`, `PUT /inventory/{id}`, `DELETE /inventory/{id}`, `GET /products/{id}/inventory` |
| Customers | `GET /customers`, `GET /customers/{id}`, `POST /customers`, `PUT /customers/{id}`, `DELETE /customers/{id}` |
| Orders | `GET /orders`, `GET /orders/{id}`, `POST /orders`, `PUT /orders/{id}/status` |

Full interactive documentation is available at `/docs` once the server is running.

## Getting Started

### Prerequisites
- Python 3.10+

### Setup

```bash
# Clone the repository
git clone https://github.com/SriLathvikaGundam/cloud-inventory-management-system.git
cd cloud-inventory-management-system

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`, with interactive docs at `http://127.0.0.1:8000/docs`.

### Example: Placing an Order

```json
POST /orders
{
  "customer_id": 1,
  "items": [
    { "product_id": 2, "quantity": 3 },
    { "product_id": 5, "quantity": 1 }
  ]
}
```

The API validates that each product exists and has sufficient stock before creating the order, then deducts the ordered quantity from inventory.

## Project Structure

```
├── main.py          # API routes and application entry point
├── models.py         # SQLAlchemy database models (tables)
├── schemas.py         # Pydantic schemas (request/response validation)
├── database.py         # Database connection and session setup
├── requirements.txt      # Python dependencies
└── README.md
```

## Deployment

Designed for deployment on Azure App Service, with the database migrated from SQLite to Azure SQL Database or Azure Database for PostgreSQL for production use.

## Future Improvements

- Authentication and role-based access control
- Pagination and filtering on list endpoints
- Automated tests (pytest)
- CI/CD pipeline for Azure deployment
