import unittest
import json
from tests.base_test import BaseTestCase


class TestFriendRoutes(BaseTestCase):
    def test_read_all_friends(self):
        self._create_test_user()
        self._create_test_user(username="frienduser1")
        self._create_test_user(username="frienduser2")
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        self.client.post(f'/api/users/{json.loads(login_response.data)["id"]}/friends/2', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        self.client.post(f'/api/users/{json.loads(login_response.data)["id"]}/friends/3', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        response = self.client.get(f'/api/users/{json.loads(login_response.data)["id"]}/friends', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['username'], 'frienduser1')
        self.assertEqual(data[1]['username'], 'frienduser2')

    def test_read_all_friends_no_friends(self):
        self._create_test_user()
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        response = self.client.get(f'/api/users/{json.loads(login_response.data)["id"]}/friends', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 0)

    def test_read_all_friends_no_jwt(self):
        self._create_test_user()
        response = self.client.get('/api/users/1/friends')
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['msg'], 'Missing Authorization Header')

    def test_read_all_friends_invalid_jwt(self):
        self._create_test_user()
        self._create_test_user(username="frienduser")
        login_response = self.client.post('/api/login', data=json.dumps({ 'username': 'testuser', 'password': 'testpassword' }), content_type='application/json')
        self.client.delete(f'/api/users/{json.loads(login_response.data)["id"]}', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        response = self.client.get(f'/api/users/{json.loads(login_response.data)["id"]}/friends', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Unauthorized')
        self.assertEqual(data['message'], 'User not found or JWT is invalid')


    def test_add_friend_no_jwt(self):
        self._create_test_user()
        response = self.client.post('/api/users/1/friends/1')
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['msg'], 'Missing Authorization Header')

    def test_add_friend_invalid_jwt(self):
        self._create_test_user()
        self._create_test_user(username="tempuser")
        self._create_test_user(username="frienduser")
        login_response = self.client.post('/api/login', data=json.dumps({ 'username': 'testuser', 'password': 'testpassword' }), content_type='application/json')
        self.client.delete(f'/api/users/{json.loads(login_response.data)["id"]}', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        response = self.client.post('/api/users/2/friends/3', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Unauthorized')
        self.assertEqual(data['message'], 'User not found or JWT is invalid')

    def test_add_friend_not_found(self):
        self._create_test_user()
        login_response = self.client.post('/api/login', data=json.dumps({ 'username': 'testuser', 'password': 'testpassword' }), content_type='application/json')
        response = self.client.post(f'/api/users/{json.loads(login_response.data)["id"]}/friends/2', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'User Not Found')
        self.assertEqual(data['message'], 'User with id 2 does not exist in the database')

    def test_add_friend_self(self):
        self._create_test_user()
        login_response = self.client.post('/api/login', data=json.dumps({ 'username': 'testuser', 'password': 'testpassword' }), content_type='application/json')
        response = self.client.post(f'/api/users/{json.loads(login_response.data)["id"]}/friends/{json.loads(login_response.data)["id"]}', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        self.assertEqual(response.status_code, 406)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Bad Request')
        self.assertEqual(data['message'], 'Cannot add yourself as a Friend')

    def test_add_friend_already_friends(self):
        self._create_test_user()
        self._create_test_user(username="frienduser")
        login_response = self.client.post('/api/login', data=json.dumps({ 'username': 'testuser', 'password': 'testpassword' }), content_type='application/json')
        self.client.post(f'/api/users/{json.loads(login_response.data)["id"]}/friends/2', headers = {'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        response = self.client.post(f'/api/users/{json.loads(login_response.data)["id"]}/friends/2', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        self.assertEqual(response.status_code, 406)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Conflict')
        self.assertEqual(data['message'], 'Already Friends with user frienduser')

    def test_delete_friend(self):
        self._create_test_user()
        self._create_test_user(username="frienduser")
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        self.client.post(f'/api/users/{json.loads(login_response.data)["id"]}/friends/2', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        response = self.client.delete(f'/api/users/{json.loads(login_response.data)["id"]}/friends/2', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Removed Friend frienduser')
        response = self.client.get(f'/api/users/{json.loads(login_response.data)["id"]}/friends', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 0)

    def test_delete_friend_not_found(self):
        self._create_test_user()
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        response = self.client.delete(f'/api/users/{json.loads(login_response.data)["id"]}/friends/2', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'User Not Found')
        self.assertEqual(data['message'], 'User with id 2 does not exist in the database')

    def test_delete_friend_no_jwt(self):
        self._create_test_user()
        response = self.client.delete('/api/users/1/friends/2')
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['msg'], 'Missing Authorization Header')

    def test_delete_friend_invalid_jwt(self):
        self._create_test_user()
        self._create_test_user(username="frienduser")
        login_response = self.client.post('/api/login', data=json.dumps({ 'username': 'testuser', 'password': 'testpassword' }), content_type='application/json')
        self.client.delete(f'/api/users/{json.loads(login_response.data)["id"]}', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        response = self.client.delete(f'/api/users/{json.loads(login_response.data)["id"]}/friends/2', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Unauthorized')
        self.assertEqual(data['message'], 'User not found or JWT is invalid')

    def test_delete_friend_not_friends(self):
        self._create_test_user()
        self._create_test_user(username="frienduser")
        login_response = self.client.post('/api/login', data=json.dumps({ 'username': 'testuser', 'password': 'testpassword' }), content_type='application/json')
        response = self.client.delete(f'/api/users/{json.loads(login_response.data)["id"]}/friends/2', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Bad request')
        self.assertEqual(data['message'], 'Not Friends with user frienduser')
