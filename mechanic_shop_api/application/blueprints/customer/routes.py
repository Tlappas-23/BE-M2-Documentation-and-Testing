from flask import request, jsonify
from marshmallow import ValidationError
from werkzeug.security import check_password_hash, generate_password_hash

from application.auth import encode_token, token_required
from application.extensions import cache, db, limiter
from application.models import Customer, ServiceTicket
from application.blueprints.customer import customer_bp
from application.blueprints.customer.schemas import (
    customer_schema,
    customers_schema,
    login_schema,
)
from application.blueprints.service_ticket.schemas import service_tickets_schema


@customer_bp.route("/", methods=["POST"])
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    password = customer_data.pop("password", None)
    if not password:
        return jsonify({"error": "Password is required."}), 400

    new_customer = Customer(**customer_data)
    new_customer.password = generate_password_hash(password)
    db.session.add(new_customer)
    db.session.commit()
    return customer_schema.jsonify(new_customer), 201


@customer_bp.route("/", methods=["GET"])
@cache.cached(timeout=60, query_string=True)
def get_customers():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    pagination = db.paginate(
        db.select(Customer).order_by(Customer.id),
        page=page,
        per_page=per_page,
        error_out=False,
    )

    return (
        jsonify(
            {
                "items": customers_schema.dump(pagination.items),
                "page": page,
                "per_page": per_page,
                "total": pagination.total,
                "pages": pagination.pages,
            }
        ),
        200,
    )


@customer_bp.route("/<int:customer_id>", methods=["GET"])
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "Customer not found."}), 404
    return customer_schema.jsonify(customer), 200


@customer_bp.route("/<int:customer_id>", methods=["PUT"])
@token_required
def update_customer(customer_id, current_customer_id):
    if current_customer_id != customer_id:
        return jsonify({"error": "Unauthorized to update this customer."}), 403

    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "Customer not found."}), 404

    try:
        customer_data = customer_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    if "password" in customer_data:
        customer.password = generate_password_hash(customer_data.pop("password"))

    for key, value in customer_data.items():
        setattr(customer, key, value)

    db.session.commit()
    return customer_schema.jsonify(customer), 200


@customer_bp.route("/<int:customer_id>", methods=["DELETE"])
@token_required
def delete_customer(customer_id, current_customer_id):
    if current_customer_id != customer_id:
        return jsonify({"error": "Unauthorized to delete this customer."}), 403

    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "Customer not found."}), 404

    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"Customer {customer_id} deleted."}), 200


@customer_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login_customer():
    try:
        credentials = login_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    customer = db.session.execute(
        db.select(Customer).where(Customer.email == credentials["email"])
    ).scalar_one_or_none()
    if not customer or not check_password_hash(customer.password, credentials["password"]):
        return jsonify({"error": "Invalid credentials."}), 401

    token = encode_token(customer.id)
    return jsonify({"token": token}), 200


@customer_bp.route("/my-tickets", methods=["GET"])
@token_required
def get_my_tickets(current_customer_id):
    tickets = db.session.scalars(
        db.select(ServiceTicket).where(ServiceTicket.customer_id == current_customer_id)
    ).all()
    return service_tickets_schema.jsonify(tickets), 200
