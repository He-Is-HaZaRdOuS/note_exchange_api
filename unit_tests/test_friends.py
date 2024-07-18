import unittest
import json
from unit_tests.base_test import BaseTestCase


class TestFriendRoutes(BaseTestCase):
    def test_read_all_friends(self):
        id_2 = self._create_test_user()
        id_3 = self._create_test_user(username="frienduser1")
        id_4 = self._create_test_user(username="frienduser2")
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        self.client.post(f'/api/users/{json.loads(login_response.data)["id"]}/friends/{id_3}', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        self.client.post(f'/api/users/{json.loads(login_response.data)["id"]}/friends/{id_4}', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        response = self.client.get(f'/api/users/{json.loads(login_response.data)["id"]}/friends', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['username'], 'frienduser1')
        self.assertEqual(data[1]['username'], 'frienduser2')

    def test_read_all_friends_no_friends(self):
        id_2 = self._create_test_user()
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        response = self.client.get(f'/api/users/{json.loads(login_response.data)["id"]}/friends', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 0)

    def test_read_all_friends_no_jwt(self):
        id_2 = self._create_test_user()
        response = self.client.get(f'/api/users/{id_2}/friends')
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['msg'], 'Missing Authorization Header')

    def test_read_all_friends_invalid_jwt(self):
        id_2 = self._create_test_user()
        id_3 = self._create_test_user(username="frienduser")
        login_response = self.client.post('/api/login', data=json.dumps({ 'username': 'testuser', 'password': 'testpassword' }), content_type='application/json')
        self.client.delete(f'/api/users/{json.loads(login_response.data)["id"]}', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        response = self.client.get(f'/api/users/{json.loads(login_response.data)["id"]}/friends', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Unauthorized')
        self.assertEqual(data['message'], 'User not found or JWT is invalid')

    def test_read_all_friends_different_user(self):
        id_2 = self._create_test_user()
        id_3 = self._create_test_user(username="frienduser")
        id_4 = self._create_test_user(username="tempuser")
        login_response = self.client.post('/api/login', data=json.dumps({ 'username': 'testuser', 'password': 'testpassword' }), content_type='application/json')
        response = self.client.get(f'/api/users/{id_4}/friends', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Forbidden')
        self.assertEqual(data['message'], 'Not authorized to access this resource')

    def test_add_friend_no_jwt(self):
        id_2 = self._create_test_user()
        id_3 = self._create_test_user(username="frienduser")
        response = self.client.post(f'/api/users/{id_2}/friends/{id_3}')
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['msg'], 'Missing Authorization Header')

    def test_add_friend_invalid_jwt(self):
        id_2 = self._create_test_user()
        id_3 = self._create_test_user(username="tempuser")
        id_4 = self._create_test_user(username="frienduser")
        login_response = self.client.post('/api/login', data=json.dumps({ 'username': 'testuser', 'password': 'testpassword' }), content_type='application/json')
        self.client.delete(f'/api/users/{json.loads(login_response.data)["id"]}', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        response = self.client.post(f'/api/users/{id_3}/friends/{id_4}', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Unauthorized')
        self.assertEqual(data['message'], 'User not found or JWT is invalid')

    def test_add_friend_not_found(self):
        id_2 = self._create_test_user()
        login_response = self.client.post('/api/login', data=json.dumps({ 'username': 'testuser', 'password': 'testpassword' }), content_type='application/json')
        response = self.client.post(f'/api/users/{json.loads(login_response.data)["id"]}/friends/{id_2+1}', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'User Not Found')
        self.assertEqual(data['message'], f'User with id {id_2+1} does not exist in the database')

    def test_add_friend_self(self):
        id_2 = self._create_test_user()
        login_response = self.client.post('/api/login', data=json.dumps({ 'username': 'testuser', 'password': 'testpassword' }), content_type='application/json')
        response = self.client.post(f'/api/users/{json.loads(login_response.data)["id"]}/friends/{json.loads(login_response.data)["id"]}', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        self.assertEqual(response.status_code, 406)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Bad Request')
        self.assertEqual(data['message'], 'Cannot add yourself as a Friend')

    def test_add_friend_already_friends(self):
        id_2 = self._create_test_user()
        id_3 = self._create_test_user(username="frienduser")
        login_response = self.client.post('/api/login', data=json.dumps({ 'username': 'testuser', 'password': 'testpassword' }), content_type='application/json')
        self.client.post(f'/api/users/{json.loads(login_response.data)["id"]}/friends/{id_3}', headers = {'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        response = self.client.post(f'/api/users/{json.loads(login_response.data)["id"]}/friends/{id_3}', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        self.assertEqual(response.status_code, 406)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Conflict')
        self.assertEqual(data['message'], 'Already Friends with user frienduser')

    def test_add_friend_different_user(self):
        id_2 = self._create_test_user()
        id_3 = self._create_test_user(username="frienduser")
        login_response = self.client.post('/api/login', data=json.dumps({ 'username': 'frienduser', 'password': 'testpassword' }), content_type='application/json')
        response = self.client.post(f'/api/users/{id_2}/friends/{id_3}', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Forbidden')
        self.assertEqual(data['message'], 'Not authorized to access this resource')

    def test_add_friend_admin(self):
        id_2 = self._create_test_user()
        id_3 = self._create_test_user(username="frienduser")
        login_response = self.client.post('/api/login', data=json.dumps({ 'username': 'superuser', 'password': 'superuser' }), content_type='application/json')
        self.client.post(f'/api/users/{id_2}/friends/{id_3}', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        response = self.client.post(f'/api/users/{id_3}/friends/{id_2}', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)

    def test_delete_friend(self):
        id_2 = self._create_test_user()
        id_3 = self._create_test_user(username="frienduser")
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        self.client.post(f'/api/users/{json.loads(login_response.data)["id"]}/friends/{id_3}', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        response = self.client.delete(f'/api/users/{json.loads(login_response.data)["id"]}/friends/{id_3}', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], f'Removed Friend with user id {id_3}')
        response = self.client.get(f'/api/users/{json.loads(login_response.data)["id"]}/friends', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 0)

    def test_delete_friend_not_found(self):
        id_2 = self._create_test_user()
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        response = self.client.delete(f'/api/users/{json.loads(login_response.data)["id"]}/friends/{id_2+1}', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'User Not Found')
        self.assertEqual(data['message'], f'User with id {id_2+1} does not exist in the database')

    def test_delete_friend_no_jwt(self):
        id_2 = self._create_test_user()
        response = self.client.delete(f'/api/users/{id_2}/friends/{id_2+1}')
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['msg'], 'Missing Authorization Header')

    def test_delete_friend_invalid_jwt(self):
        id_2 = self._create_test_user()
        id_3 = self._create_test_user(username="frienduser")
        login_response = self.client.post('/api/login', data=json.dumps({ 'username': 'testuser', 'password': 'testpassword' }), content_type='application/json')
        self.client.delete(f'/api/users/{json.loads(login_response.data)["id"]}', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        response = self.client.delete(f'/api/users/{json.loads(login_response.data)["id"]}/friends/{id_3}', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Unauthorized')
        self.assertEqual(data['message'], 'User not found or JWT is invalid')

    def test_delete_friend_not_friends(self):
        id_2 = self._create_test_user()
        id_3 = self._create_test_user(username="frienduser")
        login_response = self.client.post('/api/login', data=json.dumps({ 'username': 'testuser', 'password': 'testpassword' }), content_type='application/json')
        response = self.client.delete(f'/api/users/{json.loads(login_response.data)["id"]}/friends/{id_3}', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Bad request')
        self.assertEqual(data['message'], f'Not Friends with user id {id_3}')

    def test_delete_friend_different_user(self):
        id_2 = self._create_test_user()
        id_3 = self._create_test_user(username="frienduser")
        login_response_1 = self.client.post('/api/login', data=json.dumps({ 'username': 'testuser', 'password': 'testpassword' }), content_type='application/json')
        login_response_2 = self.client.post('/api/login', data=json.dumps({ 'username': 'frienduser', 'password': 'testpassword' }), content_type='application/json')
        self.client.post(f'/api/users/{json.loads(login_response_2.data)["id"]}/friends/{id_3}', headers={'Authorization': f'Bearer {json.loads(login_response_1.data)["access_token"]}'})
        response = self.client.delete(f'/api/users/{id_2}/friends/{id_3}', headers={'Authorization': f'Bearer {json.loads(login_response_2.data)["access_token"]}'})
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Forbidden')
        self.assertEqual(data['message'], 'Not authorized to access this resource')

    def test_delete_friend_admin(self):
        id_2 = self._create_test_user()
        id_3 = self._create_test_user(username="frienduser")
        login_response = self.client.post('/api/login', data=json.dumps({ 'username': 'superuser', 'password': 'superuser' }), content_type='application/json')
        self.client.post(f'/api/users/{id_2}/friends/{id_3}', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        response = self.client.delete(f'/api/users/{id_2}/friends/{id_3}', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], f'Removed Friend with user id {id_3}')
