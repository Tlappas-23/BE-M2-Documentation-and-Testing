from flask import request, jsonify
from marshmallow import ValidationError

from application.extensions import db
from application.models import Inventory, Mechanic, ServiceTicket
from application.blueprints.service_ticket import service_ticket_bp
from application.blueprints.service_ticket.schemas import (
    service_ticket_schema,
    service_tickets_schema,
)


@service_ticket_bp.route("/", methods=["POST"])
def create_service_ticket():
    try:
        ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_ticket = ServiceTicket(**ticket_data)
    db.session.add(new_ticket)
    db.session.commit()
    return service_ticket_schema.jsonify(new_ticket), 201


@service_ticket_bp.route("/", methods=["GET"])
def get_service_tickets():
    tickets = db.session.query(ServiceTicket).all()
    return service_tickets_schema.jsonify(tickets), 200


@service_ticket_bp.route("/<int:ticket_id>/assign-mechanic/<int:mechanic_id>", methods=["PUT"])
def assign_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not ticket or not mechanic:
        return jsonify({"error": "Service ticket or mechanic not found."}), 404

    if mechanic not in ticket.mechanics:
        ticket.mechanics.append(mechanic)
        db.session.commit()

    return service_ticket_schema.jsonify(ticket), 200


@service_ticket_bp.route("/<int:ticket_id>/remove-mechanic/<int:mechanic_id>", methods=["PUT"])
def remove_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not ticket or not mechanic:
        return jsonify({"error": "Service ticket or mechanic not found."}), 404

    if mechanic in ticket.mechanics:
        ticket.mechanics.remove(mechanic)
        db.session.commit()

    return service_ticket_schema.jsonify(ticket), 200


@service_ticket_bp.route("/<int:ticket_id>/edit", methods=["PUT"])
def edit_ticket_mechanics(ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found."}), 404

    payload = request.get_json(silent=True) or {}
    add_ids = payload.get("add_ids", [])
    remove_ids = payload.get("remove_ids", [])

    if not isinstance(add_ids, list) or not isinstance(remove_ids, list):
        return jsonify({"error": "add_ids and remove_ids must be lists."}), 400

    if add_ids:
        mechanics_to_add = db.session.scalars(
            db.select(Mechanic).where(Mechanic.id.in_(add_ids))
        ).all()
        found_ids = {mechanic.id for mechanic in mechanics_to_add}
        missing_ids = sorted(set(add_ids) - found_ids)
        if missing_ids:
            return jsonify({"error": "Mechanic(s) not found.", "missing_ids": missing_ids}), 404

        for mechanic in mechanics_to_add:
            if mechanic not in ticket.mechanics:
                ticket.mechanics.append(mechanic)

    if remove_ids:
        mechanics_to_remove = db.session.scalars(
            db.select(Mechanic).where(Mechanic.id.in_(remove_ids))
        ).all()
        found_ids = {mechanic.id for mechanic in mechanics_to_remove}
        missing_ids = sorted(set(remove_ids) - found_ids)
        if missing_ids:
            return jsonify({"error": "Mechanic(s) not found.", "missing_ids": missing_ids}), 404

        for mechanic in mechanics_to_remove:
            if mechanic in ticket.mechanics:
                ticket.mechanics.remove(mechanic)

    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200


@service_ticket_bp.route("/<int:ticket_id>/add-part/<int:inventory_id>", methods=["PUT"])
def add_part_to_ticket(ticket_id, inventory_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    inventory_item = db.session.get(Inventory, inventory_id)

    if not ticket or not inventory_item:
        return jsonify({"error": "Service ticket or inventory item not found."}), 404

    if inventory_item not in ticket.inventory_items:
        ticket.inventory_items.append(inventory_item)
        db.session.commit()

    return service_ticket_schema.jsonify(ticket), 200
