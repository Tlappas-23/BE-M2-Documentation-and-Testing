import unittest
from app import create_app
from application.models import db, Customer
from application.auth import encode_token
from werkzeug.security import generate_password_hash
from config import TestingConfig


class TestCustomers(unittest.TestCase):
    def setUp(self):
        """Set up test client and initialize test database"""
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.drop_all()
            db.create_all()

            # Create a test customer
            test_customer = Customer(
                name="Test User",
                email="test@email.com",
                password=generate_password_hash("testpass"),
                phone="123-456-7890",
                address="123 Test St"
            )
            db.session.add(test_customer)
            db.session.commit()

            # Generate token for authenticated tests
            self.token = encode_token(1)

    def tearDown(self):
        """Clean up after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # Test POST /customers/ - Create Customer
    def test_create_customer(self):
        """Test creating a new customer"""
        customer_payload = {
            "name": "John Doe",
            "email": "john@email.com",
            "password": "password123",
            "phone": "555-0100",
            "address": "456 Main St"
        }
        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "John Doe")
        self.assertEqual(response.json['email'], "john@email.com")

    def test_create_customer_missing_fields(self):
        """Test creating customer with missing required fields (negative test)"""
        customer_payload = {
            "name": "John Doe",
            "phone": "555-0100"
            # Missing email and password
        }
        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 400)

    # Test GET /customers/ - Get All Customers with Pagination
    def test_get_customers(self):
        """Test retrieving all customers with pagination"""
        response = self.client.get('/customers/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('items', response.json)
        self.assertIn('page', response.json)
        self.assertIn('total', response.json)

    def test_get_customers_with_pagination(self):
        """Test pagination parameters"""
        response = self.client.get('/customers/?page=1&per_page=5')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['per_page'], 5)

    # Test GET /customers/<id> - Get Single Customer
    def test_get_customer_by_id(self):
        """Test retrieving a single customer by ID"""
        response = self.client.get('/customers/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], "Test User")

    def test_get_customer_not_found(self):
        """Test retrieving non-existent customer (negative test)"""
        response = self.client.get('/customers/999')
        self.assertEqual(response.status_code, 404)

    # Test POST /customers/login - Login
    def test_login_customer(self):
        """Test customer login with valid credentials"""
        credentials = {
            "email": "test@email.com",
            "password": "testpass"
        }
        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials (negative test)"""
        credentials = {
            "email": "test@email.com",
            "password": "wrongpassword"
        }
        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 401)

    def test_login_missing_fields(self):
        """Test login with missing fields (negative test)"""
        credentials = {
            "email": "test@email.com"
            # Missing password
        }
        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 400)

    # Test PUT /customers/<id> - Update Customer (Protected)
    def test_update_customer(self):
        """Test updating customer with valid token"""
        update_payload = {
            "name": "Updated Name",
            "phone": "999-888-7777"
        }
        headers = {'Authorization': f"Bearer {self.token}"}
        response = self.client.put('/customers/1', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], "Updated Name")

    def test_update_customer_no_token(self):
        """Test updating customer without token (negative test)"""
        update_payload = {"name": "Updated Name"}
        response = self.client.put('/customers/1', json=update_payload)
        self.assertEqual(response.status_code, 401)

    # Test DELETE /customers/<id> - Delete Customer (Protected)
    def test_delete_customer(self):
        """Test deleting customer with valid token"""
        headers = {'Authorization': f"Bearer {self.token}"}
        response = self.client.delete('/customers/1', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('deleted', response.json['message'].lower())

    def test_delete_customer_no_token(self):
        """Test deleting customer without token (negative test)"""
        response = self.client.delete('/customers/1')
        self.assertEqual(response.status_code, 401)

    # Test GET /customers/my-tickets - Get My Tickets (Protected)
    def test_get_my_tickets(self):
        """Test retrieving logged-in customer's tickets"""
        headers = {'Authorization': f"Bearer {self.token}"}
        response = self.client.get('/customers/my-tickets', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_get_my_tickets_no_token(self):
        """Test getting tickets without token (negative test)"""
        response = self.client.get('/customers/my-tickets')
        self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()
