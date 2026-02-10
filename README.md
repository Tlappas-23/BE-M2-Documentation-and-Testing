# Mechanic Shop API

A RESTful API for managing a mechanic shop with complete Swagger documentation and comprehensive testing.

## Features

- **Customer Management** - Registration, authentication, and CRUD operations
- **Mechanic Management** - Track mechanics and their assignments
- **Service Tickets** - Manage vehicle service requests with VIN tracking
- **Inventory Management** - Track parts and pricing
- **JWT Authentication** - Secure token-based auth for customers
- **Rate Limiting** - Protection on login endpoints
- **Swagger Documentation** - Interactive API docs at `/api/docs`
- **44 Unit Tests** - Complete test coverage with positive and negative tests

## Tech Stack

- Flask 3.0.3
- Flask-SQLAlchemy
- Flask-Marshmallow
- JWT Authentication (python-jose)
- Swagger UI
- unittest

## Installation

```bash
# Clone the repository
git clone https://github.com/Tlappas-23/BE-M2-Documentation-and-Testing.git
cd BE-M2-Documentation-and-Testing/mechanic_shop_api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

## API Documentation

Access interactive Swagger documentation at: **http://127.0.0.1:5000/api/docs**

## Testing

```bash
# Run all tests
python -m unittest discover tests

# Results: 44 tests, 100% pass rate
```

## API Endpoints

### Customers (7 endpoints)
- `POST /customers/` - Register new customer
- `GET /customers/` - Get all customers (paginated)
- `GET /customers/{id}` - Get customer by ID
- `PUT /customers/{id}` - Update customer (auth required)
- `DELETE /customers/{id}` - Delete customer (auth required)
- `POST /customers/login` - Login and receive JWT token
- `GET /customers/my-tickets` - Get customer's service tickets (auth required)

### Mechanics (5 endpoints)
- `POST /mechanics/` - Create mechanic
- `GET /mechanics/` - Get all mechanics
- `GET /mechanics/by-tickets` - Get mechanics sorted by ticket count
- `PUT /mechanics/{id}` - Update mechanic
- `DELETE /mechanics/{id}` - Delete mechanic

### Service Tickets (6 endpoints)
- `POST /service-tickets/` - Create service ticket
- `GET /service-tickets/` - Get all tickets
- `PUT /service-tickets/{ticket_id}/assign-mechanic/{mechanic_id}` - Assign mechanic
- `PUT /service-tickets/{ticket_id}/remove-mechanic/{mechanic_id}` - Remove mechanic
- `PUT /service-tickets/{ticket_id}/edit` - Bulk edit mechanics
- `PUT /service-tickets/{ticket_id}/add-part/{inventory_id}` - Add inventory part

### Inventory (5 endpoints)
- `POST /inventory/` - Create inventory item
- `GET /inventory/` - Get all items
- `GET /inventory/{id}` - Get item by ID
- `PUT /inventory/{id}` - Update item
- `DELETE /inventory/{id}` - Delete item

## Authentication

Protected endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

Get a token by registering and logging in through the `/customers/` and `/customers/login` endpoints.

## Database

- **Default:** SQLite (automatically created as `app.db`)
- **Optional:** MySQL support via environment variable configuration

## Author

Thomas Lappas - [GitHub](https://github.com/Tlappas-23)
