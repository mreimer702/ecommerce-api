# E-Commerce API

## Overview
This is a RESTful API built using Flask and SQLAlchemy for managing customers, products, and orders. The API supports CRUD operations for customers, products, and orders, including the ability to add and remove products from orders.

## Features
- Create, Read, Update, and Delete (CRUD) customers
- Create, Read, Update, and Delete (CRUD) products
- Create, Read, Update, and Delete (CRUD) orders
- Add and remove products from orders
- Fetch orders for a specific user
- Fetch products in a specific order

## Technologies Used
- Python
- Flask
- SQLAlchemy
- Marshmallow (for data validation)
- SQLite/PostgreSQL (configurable database backend)

## Installation

### Clone the repository:
```sh
git clone https://github.com/yourusername/customer-order-api.git
cd customer-order-api
```

### Create and activate a virtual environment:
```sh
python -m venv venv
source venv/bin/activate  # On Windows use venv\Scripts\activate
```

### Install dependencies:
```sh
pip install -r requirements.txt
```

### Set up the database:
```sh
flask db init
flask db migrate -m "Initial migration."
flask db upgrade
```

### Run the application:
```sh
flask run
```

## API Endpoints

### Customers
- `POST /customers` - Add a new customer
- `GET /customers` - Get all customers
- `GET /customers/<id>` - Get a specific customer
- `PUT /customers/<id>` - Update customer details
- `DELETE /customers/<id>` - Delete a customer

### Products
- `POST /products` - Add a new product
- `GET /products` - Get all products
- `GET /products/<id>` - Get a specific product
- `PUT /products/<id>` - Update product details
- `DELETE /products/<id>` - Delete a product

### Orders
- `POST /orders` - Create a new order
- `PUT /orders/<order_id>/add_product/<product_id>` - Add product to an order
- `DELETE /orders/<order_id>/add_product/<product_id>` - Remove product from an order
- `GET /orders/users/<user_id>` - Get orders for a user
- `GET /orders/<order_id>/products` - Get products in an order

## Future Improvements
- Add additional endpoints for advanced order management.
- Implement pagination for user or product listings.
- Add JWT authentication for user operations.

