import unittest
import json
from tests.base_test import BaseTestCase


class TestUserRoutes(BaseTestCase):

    # def test_read_all_users(self):
    #     self._create_test_user()
    #     response = self.client.get('/api/users')
    #     self.assertEqual(response.status_code, 200)
    #     data = json.loads(response.data)
    #     self.assertEqual(len(data), 1)
    #     self.assertEqual(data[0]['username'], 'testuser')

    def test_read_user(self):
        self._create_test_user()
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        response = self.client.get(f'/api/users/{json.loads(login_response.data)["id"]}', headers={'Authorization': f'Bearer testuser{json.loads(login_response.data)["access_token"]}'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['username'], 'testuser')

    def test_read_user_not_found(self):
        response = self.client.get('/api/users/1')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'User Not Found')
        self.assertEqual(data['message'], 'User with id 1 does not exist in the database')

    def test_update_user(self):
        self._create_test_user()
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        response = self.client.put(f'/api/users/{json.loads(login_response.data)["id"]}', data=json.dumps({
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
        response = self.client.put('/api/users/2', data=json.dumps({
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
        response = self.client.put('/api/users/2', data=json.dumps({
            'password': 'newpassword'
        }), headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'User Not Found')
        self.assertEqual(data['message'], 'User with id 2 does not exist in the database')

    def test_update_user_invalid_jwt(self):
        self._create_test_user()
        self._create_test_user(username='tempuser', password='temppassword')
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        self.client.delete(f'/api/users/{json.loads(login_response.data)["id"]}', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        response = self.client.put(f'/api/users/{json.loads(login_response.data)["id"]}', data=json.dumps({
            'password': 'newpassword'
        }), headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
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
        response = self.client.put(f'/api/users/{json.loads(login_response.data)["id"]}', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
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
        response = self.client.put(f'/api/users/{json.loads(login_response.data)["access_token"]}', data=json.dumps({
            'wrongkey': 'newpassword'
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
        response = self.client.delete(f'/api/users/{json.loads(login_response.data)["id"]}', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        self.assertEqual(response.status_code, 200)

    def test_delete_user_invalid_jwt(self):
        self._create_test_user()
        self._create_test_user(username='tempuser', password='temppassword')
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'tempuser',
            'password': 'temppassword'
        }), content_type='application/json')
        self.client.delete(f'/api/users/{json.loads(login_response.data)["id"]}', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        response = self.client.delete('/api/users/1', headers={'Authorization' : f'Bearer {json.loads(login_response.data)["access_token"]}'})
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
        response = self.client.delete('/api/users/2', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
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
        response = self.client.delete('/api/users/2', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'User Not Found')
        self.assertEqual(data['message'], 'User with id 2 does not exist in the database')
