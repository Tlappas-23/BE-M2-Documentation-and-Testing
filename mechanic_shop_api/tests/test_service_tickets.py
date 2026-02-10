import unittest
from app import create_app
from application.models import db, Customer, Mechanic, ServiceTicket, Inventory
from config import TestingConfig


class TestServiceTickets(unittest.TestCase):
    def setUp(self):
        """Set up test client and initialize test database"""
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.drop_all()
            db.create_all()

            # Create test customer
            customer = Customer(
                name="Test Customer",
                email="customer@test.com",
                password="password",
                phone="555-1000"
            )
            db.session.add(customer)

            # Create test mechanics
            mechanic1 = Mechanic(
                name="Mechanic One",
                email="mech1@test.com",
                phone="555-2000"
            )
            mechanic2 = Mechanic(
                name="Mechanic Two",
                email="mech2@test.com",
                phone="555-3000"
            )
            db.session.add(mechanic1)
            db.session.add(mechanic2)

            # Create test inventory item
            part = Inventory(
                name="Oil Filter",
                price=12.99
            )
            db.session.add(part)

            # Create test service ticket
            ticket = ServiceTicket(
                description="Oil change",
                vin="1HGCM82633A123456",
                customer_id=1
            )
            db.session.add(ticket)
            db.session.commit()

    def tearDown(self):
        """Clean up after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # Test POST /service-tickets/ - Create Service Ticket
    def test_create_service_ticket(self):
        """Test creating a new service ticket"""
        ticket_payload = {
            "description": "Brake repair",
            "vin": "2FMDK4KC8DBA12345",
            "customer_id": 1
        }
        response = self.client.post('/service-tickets/', json=ticket_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['description'], "Brake repair")

    def test_create_service_ticket_missing_fields(self):
        """Test creating ticket with missing fields (negative test)"""
        ticket_payload = {
            "description": "Brake repair"
            # Missing vin and customer_id
        }
        response = self.client.post('/service-tickets/', json=ticket_payload)
        self.assertEqual(response.status_code, 400)

    # Test GET /service-tickets/ - Get All Service Tickets
    def test_get_service_tickets(self):
        """Test retrieving all service tickets"""
        response = self.client.get('/service-tickets/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertEqual(len(response.json), 1)

    # Test PUT /service-tickets/<id>/assign-mechanic/<mechanic_id>
    def test_assign_mechanic_to_ticket(self):
        """Test assigning a mechanic to a service ticket"""
        response = self.client.put('/service-tickets/1/assign-mechanic/1')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json['mechanics']) > 0)

    def test_assign_mechanic_ticket_not_found(self):
        """Test assigning mechanic to non-existent ticket (negative test)"""
        response = self.client.put('/service-tickets/999/assign-mechanic/1')
        self.assertEqual(response.status_code, 404)

    # Test PUT /service-tickets/<id>/remove-mechanic/<mechanic_id>
    def test_remove_mechanic_from_ticket(self):
        """Test removing a mechanic from a service ticket"""
        # First assign a mechanic
        self.client.put('/service-tickets/1/assign-mechanic/1')

        # Then remove the mechanic
        response = self.client.put('/service-tickets/1/remove-mechanic/1')
        self.assertEqual(response.status_code, 200)

    def test_remove_mechanic_not_found(self):
        """Test removing mechanic from non-existent ticket (negative test)"""
        response = self.client.put('/service-tickets/999/remove-mechanic/1')
        self.assertEqual(response.status_code, 404)

    # Test PUT /service-tickets/<id>/edit - Bulk Edit Mechanics
    def test_bulk_edit_mechanics(self):
        """Test bulk adding and removing mechanics"""
        payload = {
            "add_ids": [1, 2],
            "remove_ids": []
        }
        response = self.client.put('/service-tickets/1/edit', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['mechanics']), 2)

    def test_bulk_edit_invalid_payload(self):
        """Test bulk edit with invalid payload (negative test)"""
        payload = {
            "add_ids": "not a list",  # Should be a list
            "remove_ids": []
        }
        response = self.client.put('/service-tickets/1/edit', json=payload)
        self.assertEqual(response.status_code, 400)

    def test_bulk_edit_missing_mechanic_ids(self):
        """Test bulk edit with non-existent mechanic IDs (negative test)"""
        payload = {
            "add_ids": [999, 888],
            "remove_ids": []
        }
        response = self.client.put('/service-tickets/1/edit', json=payload)
        self.assertEqual(response.status_code, 404)

    # Test PUT /service-tickets/<id>/add-part/<inventory_id>
    def test_add_part_to_ticket(self):
        """Test adding an inventory part to a service ticket"""
        response = self.client.put('/service-tickets/1/add-part/1')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json['inventory_items']) > 0)

    def test_add_part_ticket_not_found(self):
        """Test adding part to non-existent ticket (negative test)"""
        response = self.client.put('/service-tickets/999/add-part/1')
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
