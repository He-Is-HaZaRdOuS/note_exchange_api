import unittest
import json
from tests.base_test import BaseTestCase

class TestAuthenticationRoutes(BaseTestCase):

    def test_register(self):
        response = self.client.post('/api/register', data=json.dumps({
            'username': 'newuser',
            'password': 'newpassword'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['username'], 'newuser')

    def test_register_existing(self):
        self._create_test_user()
        response = self.client.post('/api/register', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 406)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Username already in use')
        self.assertEqual(data['message'], 'User with username testuser already exists')

    def test_register_invalid_json(self):
        response = self.client.post('/api/register', data=json.dumps({
            'username': 'newuser'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Bad Request')
        self.assertEqual(data['message'], 'Invalid JSON body')

    def test_register_no_json(self):
        response = self.client.post('/api/register')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Bad Request')
        self.assertEqual(data['message'], 'Could not load JSON from request')

    def test_login(self):
        self._create_test_user()
        response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data)

    def test_login_invalid(self):
        response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'wrongpassword'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Unauthorized')
        self.assertEqual(data['message'], 'Invalid credentials')

    def test_login_no_json(self):
        response = self.client.post('/api/login')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Bad Request')
        self.assertEqual(data['message'], 'Could not load JSON from request')

    def test_login_invalid_json(self):
        response = self.client.post('/api/login', data=json.dumps({
            'password': 'testpassword'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Bad Request')
        self.assertEqual(data['message'], 'Invalid JSON body')

if __name__ == '__main__':
    unittest.main()
