from marshmallow import fields

from application.blueprints.inventory.schemas import InventorySchema
from application.blueprints.mechanic.schemas import MechanicSchema
from application.extensions import ma
from application.models import ServiceTicket


class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    mechanics = fields.Nested(MechanicSchema, many=True, dump_only=True)
    inventory_items = fields.Nested(InventorySchema, many=True, dump_only=True)

    class Meta:
        model = ServiceTicket
        load_instance = False
        include_fk = True


service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
