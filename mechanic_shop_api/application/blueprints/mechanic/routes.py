from flask import request, jsonify
from marshmallow import ValidationError

from application.extensions import db
from application.models import Mechanic, service_ticket_mechanic
from application.blueprints.mechanic import mechanic_bp
from application.blueprints.mechanic.schemas import mechanic_schema, mechanics_schema


@mechanic_bp.route("/", methods=["POST"])
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_mechanic = Mechanic(**mechanic_data)
    db.session.add(new_mechanic)
    db.session.commit()
    return mechanic_schema.jsonify(new_mechanic), 201


@mechanic_bp.route("/", methods=["GET"])
def get_mechanics():
    mechanics = db.session.query(Mechanic).all()
    return mechanics_schema.jsonify(mechanics), 200


@mechanic_bp.route("/by-tickets", methods=["GET"])
def get_mechanics_by_tickets():
    mechanics = (
        db.session.query(Mechanic)
        .outerjoin(
            service_ticket_mechanic,
            Mechanic.id == service_ticket_mechanic.c.mechanic_id,
        )
        .group_by(Mechanic.id)
        .order_by(db.func.count(service_ticket_mechanic.c.service_ticket_id).desc())
        .all()
    )
    return mechanics_schema.jsonify(mechanics), 200


@mechanic_bp.route("/<int:mechanic_id>", methods=["PUT"])
def update_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    try:
        mechanic_data = mechanic_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in mechanic_data.items():
        setattr(mechanic, key, value)

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200


@mechanic_bp.route("/<int:mechanic_id>", methods=["DELETE"])
def delete_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f"Mechanic {mechanic_id} deleted."}), 200
