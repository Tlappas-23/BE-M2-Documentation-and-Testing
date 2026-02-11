import unittest
from application import create_app
from application.models import db, Mechanic
from config import TestingConfig


class TestMechanics(unittest.TestCase):
    def setUp(self):
        """Set up test client and initialize test database"""
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.drop_all()
            db.create_all()

            # Create test mechanics
            mechanic1 = Mechanic(
                name="Mike Johnson",
                email="mike@mechanic.com",
                phone="555-0100",
                address="789 Shop St",
                salary=55000.00
            )
            mechanic2 = Mechanic(
                name="Sarah Williams",
                email="sarah@mechanic.com",
                phone="555-0200",
                address="321 Garage Ave",
                salary=60000.00
            )
            db.session.add(mechanic1)
            db.session.add(mechanic2)
            db.session.commit()

    def tearDown(self):
        """Clean up after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # Test POST /mechanics/ - Create Mechanic
    def test_create_mechanic(self):
        """Test creating a new mechanic"""
        mechanic_payload = {
            "name": "Tom Davis",
            "email": "tom@mechanic.com",
            "phone": "555-0300",
            "address": "111 Auto Ln",
            "salary": 58000.00
        }
        response = self.client.post('/mechanics/', json=mechanic_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "Tom Davis")
        self.assertEqual(response.json['email'], "tom@mechanic.com")

    def test_create_mechanic_missing_fields(self):
        """Test creating mechanic with missing required fields (negative test)"""
        mechanic_payload = {
            "name": "Tom Davis",
            "phone": "555-0300"
            # Missing email (required field)
        }
        response = self.client.post('/mechanics/', json=mechanic_payload)
        self.assertEqual(response.status_code, 400)

    # Test GET /mechanics/ - Get All Mechanics
    def test_get_mechanics(self):
        """Test retrieving all mechanics"""
        response = self.client.get('/mechanics/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertEqual(len(response.json), 2)

    # Test GET /mechanics/by-tickets - Get Mechanics by Ticket Count
    def test_get_mechanics_by_tickets(self):
        """Test retrieving mechanics sorted by ticket count"""
        response = self.client.get('/mechanics/by-tickets')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    # Test PUT /mechanics/<id> - Update Mechanic
    def test_update_mechanic(self):
        """Test updating a mechanic"""
        update_payload = {
            "name": "Mike Johnson Updated",
            "salary": 58000.00
        }
        response = self.client.put('/mechanics/1', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], "Mike Johnson Updated")
        self.assertEqual(response.json['salary'], 58000.00)

    def test_update_mechanic_not_found(self):
        """Test updating non-existent mechanic (negative test)"""
        update_payload = {"name": "Nobody"}
        response = self.client.put('/mechanics/999', json=update_payload)
        self.assertEqual(response.status_code, 404)

    # Test DELETE /mechanics/<id> - Delete Mechanic
    def test_delete_mechanic(self):
        """Test deleting a mechanic"""
        response = self.client.delete('/mechanics/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn('deleted', response.json['message'].lower())

    def test_delete_mechanic_not_found(self):
        """Test deleting non-existent mechanic (negative test)"""
        response = self.client.delete('/mechanics/999')
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
