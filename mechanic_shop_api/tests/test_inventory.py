import unittest
from app import create_app
from application.models import db, Inventory
from config import TestingConfig


class TestInventory(unittest.TestCase):
    def setUp(self):
        """Set up test client and initialize test database"""
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.drop_all()
            db.create_all()

            # Create test inventory items
            item1 = Inventory(name="Oil Filter", price=12.99)
            item2 = Inventory(name="Brake Pads", price=45.50)
            item3 = Inventory(name="Air Filter", price=18.75)

            db.session.add(item1)
            db.session.add(item2)
            db.session.add(item3)
            db.session.commit()

    def tearDown(self):
        """Clean up after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # Test POST /inventory/ - Create Inventory Item
    def test_create_inventory_item(self):
        """Test creating a new inventory item"""
        item_payload = {
            "name": "Spark Plugs",
            "price": 29.99
        }
        response = self.client.post('/inventory/', json=item_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "Spark Plugs")
        self.assertEqual(response.json['price'], 29.99)

    def test_create_inventory_missing_fields(self):
        """Test creating inventory item with missing fields (negative test)"""
        item_payload = {
            "name": "Spark Plugs"
            # Missing price (required field)
        }
        response = self.client.post('/inventory/', json=item_payload)
        self.assertEqual(response.status_code, 400)

    # Test GET /inventory/ - Get All Inventory Items
    def test_get_inventory_items(self):
        """Test retrieving all inventory items"""
        response = self.client.get('/inventory/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertEqual(len(response.json), 3)

    # Test GET /inventory/<id> - Get Single Inventory Item
    def test_get_inventory_item_by_id(self):
        """Test retrieving a single inventory item by ID"""
        response = self.client.get('/inventory/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], "Oil Filter")

    def test_get_inventory_item_not_found(self):
        """Test retrieving non-existent inventory item (negative test)"""
        response = self.client.get('/inventory/999')
        self.assertEqual(response.status_code, 404)

    # Test PUT /inventory/<id> - Update Inventory Item
    def test_update_inventory_item(self):
        """Test updating an inventory item"""
        update_payload = {
            "name": "Premium Oil Filter",
            "price": 15.99
        }
        response = self.client.put('/inventory/1', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], "Premium Oil Filter")
        self.assertEqual(response.json['price'], 15.99)

    def test_update_inventory_item_not_found(self):
        """Test updating non-existent inventory item (negative test)"""
        update_payload = {"name": "Nonexistent"}
        response = self.client.put('/inventory/999', json=update_payload)
        self.assertEqual(response.status_code, 404)

    # Test DELETE /inventory/<id> - Delete Inventory Item
    def test_delete_inventory_item(self):
        """Test deleting an inventory item"""
        response = self.client.delete('/inventory/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn('deleted', response.json['message'].lower())

    def test_delete_inventory_item_not_found(self):
        """Test deleting non-existent inventory item (negative test)"""
        response = self.client.delete('/inventory/999')
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
