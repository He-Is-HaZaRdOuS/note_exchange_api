import unittest
import json
from tests.base_test import BaseTestCase

class TestAuthenticationRoutes(BaseTestCase):

    def test_read_all_users(self):
        self._create_test_user()
        response = self.client.get('/api/users')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['username'], 'testuser')

    def test_read_user(self):
        self._create_test_user()
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        response = self.client.get('/api/users/testuser', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['username'], 'testuser')

    def test_read_user_not_found(self):
        response = self.client.get('/api/users/testuser')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'User Not Found')
        self.assertEqual(data['message'], 'User with username testuser does not exist in the database')

    def test_update_user(self):
        self._create_test_user()
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        response = self.client.put('/api/users', data=json.dumps({
            'username': 'testuser',
            'password': 'newpassword'
        }), headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['username'], 'testuser')

    def test_update_user_different_user(self):
        self._create_test_user()
        self._create_test_user(username='wronguser', password='testpassword')
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        response = self.client.put('/api/users', data=json.dumps({
            'username': 'wronguser',
            'password': 'newpassword'
        }), headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Forbidden')
        self.assertEqual(data['message'], 'Not authorized to access this resource')

    def test_update_wrong_user(self):
        self._create_test_user()
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        response = self.client.put('/api/users', data=json.dumps({
            'username': 'wronguser',
            'password': 'newpassword'
        }), headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'User Not Found')
        self.assertEqual(data['message'], 'User with username wronguser does not exist in the database')

    def test_update_user_invalid_jwt(self):
        self._create_test_user
        response = self.client.put('/api/users', data=json.dumps({
            'username': 'wronguser',
            'password': 'newpassword'
        }), headers={'Authorization': f'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcyMDg5NDEzNiwianRpIjoiMzJhY2FjYTMtMjAzOC00YjAyLWE2YTEtNWJiMDkzOTBhNzQzIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6eyJ1c2VybmFtZSI6Im5vdXNlciJ9LCJuYmYiOjE3MjA4OTQxMzYsImNzcmYiOiIzMGQ1YThkOC1kMzVlLTQyZjktYmY1ZS0xM2YwYTg3MWI1YjMiLCJleHAiOjE3MjA5ODA1MzZ9.MiHCygDrGyxTfOUP_OIus6so_hBzvN03O3DWGVz9F_Y'}, content_type='application/json')
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Unauthorized')
        self.assertEqual(data['message'], 'User not found or JWT is invalid')

    def test_update_user_no_json(self):
        self._create_test_user()
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        response = self.client.put('/api/users', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Bad Request')
        self.assertEqual(data['message'], 'Could not load JSON from request')

    def test_update_user_invalid_json(self):
        self._create_test_user()
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        response = self.client.put('/api/users', data=json.dumps({
            'wrongkey': 'testuser',
            'password': 'newpassword'
        }), headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Bad Request')
        self.assertEqual(data['message'], 'Invalid JSON body')

    def test_delete_user(self):
        self._create_test_user()
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        response = self.client.delete('/api/users/testuser', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        print(response.data)
        self.assertEqual(response.status_code, 200)

    def test_delete_user_invalid_jwt(self):
        self._create_test_user()
        response = self.client.delete('/api/users/testuser', headers={'Authorization' : f'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcyMDg5NDEzNiwianRpIjoiMzJhY2FjYTMtMjAzOC00YjAyLWE2YTEtNWJiMDkzOTBhNzQzIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6eyJ1c2VybmFtZSI6Im5vdXNlciJ9LCJuYmYiOjE3MjA4OTQxMzYsImNzcmYiOiIzMGQ1YThkOC1kMzVlLTQyZjktYmY1ZS0xM2YwYTg3MWI1YjMiLCJleHAiOjE3MjA5ODA1MzZ9.MiHCygDrGyxTfOUP_OIus6so_hBzvN03O3DWGVz9F_Y'})
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Unauthorized')
        self.assertEqual(data['message'], 'User not found or JWT is invalid')

    def test_delete_user_different_user(self):
        self._create_test_user()
        self._create_test_user(username='wronguser', password='testpassword')
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        response = self.client.delete('/api/users/wronguser', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Forbidden')
        self.assertEqual(data['message'], 'Not authorized to access this resource')

    def test_delete_user_not_found(self):
        self._create_test_user()
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        response = self.client.delete('/api/users/wronguser', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'User Not Found')
        self.assertEqual(data['message'], 'User with username wronguser does not exist in the database')
