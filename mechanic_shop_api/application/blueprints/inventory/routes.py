from flask import jsonify, request
from marshmallow import ValidationError

from application.blueprints.inventory import inventory_bp
from application.blueprints.inventory.schemas import (
    inventories_schema,
    inventory_schema,
)
from application.extensions import db
from application.models import Inventory


@inventory_bp.route("/", methods=["POST"])
def create_inventory_item():
    try:
        inventory_data = inventory_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_item = Inventory(**inventory_data)
    db.session.add(new_item)
    db.session.commit()
    return inventory_schema.jsonify(new_item), 201


@inventory_bp.route("/", methods=["GET"])
def get_inventory_items():
    items = db.session.query(Inventory).all()
    return inventories_schema.jsonify(items), 200


@inventory_bp.route("/<int:inventory_id>", methods=["GET"])
def get_inventory_item(inventory_id):
    item = db.session.get(Inventory, inventory_id)
    if not item:
        return jsonify({"error": "Inventory item not found."}), 404
    return inventory_schema.jsonify(item), 200


@inventory_bp.route("/<int:inventory_id>", methods=["PUT"])
def update_inventory_item(inventory_id):
    item = db.session.get(Inventory, inventory_id)
    if not item:
        return jsonify({"error": "Inventory item not found."}), 404

    try:
        inventory_data = inventory_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in inventory_data.items():
        setattr(item, key, value)

    db.session.commit()
    return inventory_schema.jsonify(item), 200


@inventory_bp.route("/<int:inventory_id>", methods=["DELETE"])
def delete_inventory_item(inventory_id):
    item = db.session.get(Inventory, inventory_id)
    if not item:
        return jsonify({"error": "Inventory item not found."}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": f"Inventory item {inventory_id} deleted."}), 200
