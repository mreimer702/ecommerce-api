from __future__ import annotations
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_marshmallow import Marshmallow
from datetime import date
from typing import List
from marshmallow import ValidationError, fields
from sqlalchemy import select, delete

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:MRYW%405172020@localhost/ecommerce_api'

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(app, model_class=Base)
ma = Marshmallow(app)

#============================ MODELS =============================

class Customer(Base):
    __tablename__ = 'customer'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(225), nullable=False)
    email: Mapped[str] = mapped_column(db.String(225))
    address: Mapped[str] = mapped_column(db.String(225))
    orders: Mapped[List["Orders"]] = db.relationship(back_populates='customer')
    
order_products = db.Table(
    "Order_Products",
    Base.metadata,
    db.Column('order_id', db.ForeignKey('orders.id')),
    db.Column('product_id', db.ForeignKey('products.id'))
)
    
class Orders(Base):
    __tablename__ = 'orders'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    order_date: Mapped[date] = mapped_column(db.Date, nullable=False)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey('customer.id'))
    customer: Mapped['Customer'] = db.relationship('Customer', back_populates='orders')
    products: Mapped[List['Products']] = db.relationship('Products', secondary=order_products, back_populates="orders")
    
class Products(Base):
    __tablename__ = 'products'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    price: Mapped[float] = mapped_column(db.Float, nullable=False)
    orders: Mapped[List['Orders']] = db.relationship(secondary=order_products, back_populates="products")
    
with app.app_context():
    db.create_all()
    
#=================================== Schemas ================================

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        include_relationships = True

class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Products

class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Orders
        
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)


#=============================== Customer CRUD ==============================

@app.route("/customers", methods=["POST"])
def add_customer():
    
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_customer = Customer(name=customer_data["name"], email=customer_data["email"], address=customer_data["address"])
    db.session.add(new_customer)
    db.session.commit()
    
    return jsonify({"Message": "New Customer added successfully",
                    "customer": customer_schema.dump(new_customer)}), 201
    
@app.route("/customers", methods=["GET"])
def get_customers():
    customers = db.session.scalars(select(Customer)).all()
    return jsonify(customers_schema.dump(customers))

@app.route("/customers/<int:id>", methods=["GET"])
def get_customers_by_id(id):
    
    query = select(Customer).where(Customer.id==id)
    result = db.session.execute(query).scalar_one_or_none()
    if result is None:
        return jsonify({"error": "Customer not found"}), 404  
    return customer_schema.jsonify(result)  

@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = db.session.get(Customer, id)

    if not customer:
        return jsonify({"message": "Invalid customer id"}), 400
    
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    customer.name = customer_data['name']
    customer.email = customer_data['email']
    customer.address = customer_data['address']

    db.session.commit()
    return jsonify(customer_schema.dump(customer)), 200

@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = db.session.get(Customer, id)

    if not customer:
        return jsonify({"message": "Customer not found"}), 404
    
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"succefully deleted customer {id}"}), 200

#=============================== Product CRUD ==============================

@app.route("/products", methods=["POST"])
def add_product():
    
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_product = Products(name=product_data["name"], price=product_data["price"])
    db.session.add(new_product)
    db.session.commit()
    
    return jsonify({"Message": "New Product added successfully",
                "product": product_schema.dump(new_product)}), 201
    
@app.route("/products", methods=["GET"])
def get_products():
    
    query = select(Products)
    result = db.session.execute(query).scalars()
    products = result.all()
    return products_schema.jsonify(products)

@app.route("/products/<int:id>", methods=["GET"])
def get_products_by_id(id):
    
    query = select(Products).where(Products.id==id)
    result = db.session.execute(query).scalar_one_or_none()
    if result is None:
        return jsonify({"error": "Product not found"}), 404  
    return product_schema.jsonify(result)  

@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = db.session.get(Products, id)

    if not product:
        return jsonify({"message": "Invalid product id"}), 400
    
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    product.name = product_data['name']
    product.price = product_data['price']

    db.session.commit()
    return jsonify(product_schema.dump(product)), 200

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = db.session.get(Products, id)

    if not product:
        return jsonify({"message": "Product not found"}), 404
    
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": f"succefully deleted product {id}"}), 200

#=============================== Order CRUD ==============================

@app.route("/orders", methods=["POST"])
def add_order():
    
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_order = Orders(order_date=order_data["order_date"], user_id=order_data["user_id"])
    db.session.add(new_order)
    db.session.commit()
    
    return jsonify({"Message": "New Order added successfully",
                    "customer": order_schema.dump(new_order)}), 201

@app.route('/orders/<int:order_id>/add_product/<int:product_id>', methods=['PUT'])
def add_product_to_order(order_id, product_id):
    order = db.session.get(Orders, order_id)
    if not order:
        return jsonify({"message": "Invalid order ID"}), 400

    product = db.session.get(Products, product_id)
    if not product:
        return jsonify({"message": "Invalid product ID"}), 400

    existing_order_product = db.session.execute(
        select(order_products).where(
            (order_products.c.order_id == order_id) & (order_products.c.product_id == product_id)
        )
    ).scalar_one_or_none()

    if existing_order_product:
        return jsonify({"message": "Product is already in the order"}), 400

    new_order_product = order_products.insert().values(order_id=order_id, product_id=product_id)
    db.session.execute(new_order_product)
    db.session.commit()

    return jsonify({
        "message": "Product added to order successfully",
        "order_id": order_id,
        "product_id": product_id
    }), 200

@app.route('/orders/<int:order_id>/add_product/<int:product_id>', methods=['DELETE'])
def delete_product_from_order(order_id, product_id):
    order = db.session.get(Orders, order_id)
    if not order:
        return jsonify({"message": "Invalid order ID"}), 400

    product = db.session.get(Products, product_id)
    if not product:
        return jsonify({"message": "Invalid product ID"}), 400

    order_product = db.session.execute(
        select(order_products).where(
            (order_products.c.order_id == order_id) & (order_products.c.product_id == product_id)
        )
    ).scalar_one_or_none()

    if not order_product:
        return jsonify({"message": "Product is not in the order"}), 400

    db.session.execute(
        delete(order_products).where(
            (order_products.c.order_id == order_id) & (order_products.c.product_id == product_id)
        )
    )
    db.session.commit()

    return jsonify({"message": f"Successfully deleted product {product_id} from order {order_id}"}), 200

@app.route("/orders/users/<int:user_id>", methods=["GET"])
def get_user_orders(user_id):
    query = select(Orders).where(Orders.customer_id == user_id)
    result = db.session.execute(query).scalars().all()

    if not result:
        return jsonify({"error": f"No orders found for user {user_id}"}), 404

    return orders_schema.jsonify(result)

@app.route("/orders/<int:order_id>/products", methods=["GET"])
def get_products_in_order(order_id):
    query = (
        select(Products)
        .join(order_products, order_products.c.product_id == Products.id)
        .where(order_products.c.order_id == order_id)
    )
    
    result = db.session.execute(query).scalars().all()

    if not result:
        return jsonify({"error": f"No products found in order {order_id}"}), 404

    return products_schema.jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5001)