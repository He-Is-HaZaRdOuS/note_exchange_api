import unittest
import json
from tests.base_test import BaseTestCase


class TestNoteRoutes(BaseTestCase):

    def test_create_note(self):
        self._create_test_user()
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        response = self.client.post(f'/api/users/{json.loads(login_response.data)["id"]}/notes', data=json.dumps({'content': 'testcontent'}), headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['content'], 'testcontent')
        self.assertIn('timestamp', data)
        self.assertIn('id', data)
        self.assertIn('user_id', data)

    def test_create_note_invalid_jwt(self):
        self._create_test_user()
        self._create_test_user(username='tempuser', password='temppassword')
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'tempuser',
            'password': 'temppassword'
        }), content_type='application/json')
        self.client.delete(f'/api/users/{json.loads(login_response.data)["id"]}', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        response = self.client.post('/api/users/1/notes', data=json.dumps({'content': 'testcontent'}),  headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Unauthorized')
        self.assertEqual(data['message'], 'User not found or JWT is invalid')

    def test_create_note_user_not_found(self):
        self._create_test_user()
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        response = self.client.post(f'/api/users/100/notes', data=json.dumps({'content': 'testcontent'}), headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'User Not Found')
        self.assertEqual(data['message'], 'User with id 100 does not exist in the database')

    def test_create_note_no_json(self):
        self._create_test_user()
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        response = self.client.post(f'/api/users/{json.loads(login_response.data)["id"]}/notes', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Bad Request')
        self.assertEqual(data['message'], 'Could not load JSON from request')

    def test_create_note_invalid_json(self):
        self._create_test_user()
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        response = self.client.post(f'/api/users/{json.loads(login_response.data)["id"]}/notes', data=json.dumps({'wrongkey': 'jibberish'}), headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Bad Request')
        self.assertEqual(data['message'], 'Invalid JSON body')

    def test_create_note_different_user(self):
        self._create_test_user()
        self._create_test_user('testuser2', 'testpassword2')
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser2',
            'password': 'testpassword2'
        }), content_type='application/json')
        response = self.client.post(f'/api/users/1/notes', data=json.dumps({'content': 'testcontent'}), headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Forbidden')
        self.assertEqual(data['message'], 'Not authorized to access this resource')

    def test_get_note(self):
        self._create_test_user()
        self._create_test_note(1, 'testcontent')
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        response = self.client.get(f'/api/users/{json.loads(login_response.data)["id"]}/notes/1', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['content'], 'testcontent')
        self.assertIn('timestamp', data)
        self.assertIn('id', data)
        self.assertIn('user_id', data)

    def test_get_note_user_not_found(self):
        self._create_test_user()
        self._create_test_note(1, 'testcontent')
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        response = self.client.get(f'/api/users/2/notes/1', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'User Not Found')
        self.assertEqual(data['message'], 'User with id 2 does not exist in the database')

    def test_get_note_different_user(self):
        self._create_test_user()
        self._create_test_note(1, 'testcontent')
        self._create_test_user('testuser2', 'testpassword2')
        self._create_test_note(2, 'testcontent2')
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        response = self.client.get(f'/api/users/2/notes/2', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Forbidden')
        self.assertEqual(data['message'], 'Not authorized to access this resource')

    def test_get_note_invalid_jwt(self):
        self._create_test_user()
        self._create_test_note(1, 'testcontent')
        self._create_test_user(username='tempuser', password='temppassword')
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'tempuser',
            'password': 'temppassword'
        }), content_type='application/json')
        self.client.delete(f'/api/users/{json.loads(login_response.data)["id"]}', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        response = self.client.get(f'/api/users/{json.loads(login_response.data)["id"]}/notes/1', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Unauthorized')
        self.assertEqual(data['message'], 'User not found or JWT is invalid')

    def test_get_note_not_found(self):
        self._create_test_user()
        self._create_test_note(1, 'testcontent')
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        response = self.client.get(f'/api/users/{json.loads(login_response.data)["id"]}/notes/2', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Note not found')
        self.assertEqual(data['message'], 'Note with id 2 does not exist in the database')

    def test_get_notes(self):
        self._create_test_user()
        self._create_test_note(1, 'testcontent')
        self._create_test_note(1, 'testcontent2')
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        response = self.client.get(f'/api/users/{json.loads(login_response.data)["id"]}/notes', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['content'], 'testcontent')
        self.assertEqual(data[1]['content'], 'testcontent2')
        self.assertIn('timestamp', data[0])
        self.assertIn('id', data[0])
        self.assertIn('user_id', data[0])

    def test_get_notes_invalid_jwt(self):
        self._create_test_user()
        self._create_test_note(1, 'testcontent')
        self._create_test_note(1, 'testcontent2')
        self._create_test_user('testuser2', 'testpassword2')
        self._create_test_note(2, 'testcontent3')
        self._create_test_note(2, 'testcontent4')
        self._create_test_user(username='tempuser', password='temppassword')
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'tempuser',
            'password': 'temppassword'
        }), content_type='application/json')
        self.client.delete(f'/api/users/{json.loads(login_response.data)["id"]}', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        response = self.client.get(f'/api/users/{json.loads(login_response.data)["id"]}/notes',headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Unauthorized')
        self.assertEqual(data['message'], 'User not found or JWT is invalid')

    def test_get_notes_user_not_found(self):
        self._create_test_user()
        self._create_test_note(1, 'testcontent')
        self._create_test_note(1, 'testcontent2')
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        response = self.client.get(f'/api/users/2/notes', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'User Not Found')
        self.assertEqual(data['message'], 'User with id 2 does not exist in the database')

    def test_get_notes_different_user(self):
        self._create_test_user()
        self._create_test_note(1, 'testcontent')
        self._create_test_note(1, 'testcontent2')
        self._create_test_user('testuser2', 'testpassword2')
        self._create_test_note(2, 'testcontent3')
        self._create_test_note(2, 'testcontent4')
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        response = self.client.get(f'/api/users/2/notes', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Forbidden')
        self.assertEqual(data['message'], 'Not authorized to access this resource')

    def test_update_note(self):
        self._create_test_user()
        self._create_test_note(1, 'testcontent')
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        response = self.client.put(f'/api/users/{json.loads(login_response.data)["id"]}/notes/1', data=json.dumps({'content': 'newcontent'}), headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['content'], 'newcontent')
        self.assertIn('timestamp', data)
        self.assertIn('id', data)
        self.assertIn('user_id', data)

    def test_update_note_different_owner(self):
        self._create_test_user()
        self._create_test_user('testuser2', 'testpassword2')
        self._create_test_note(1, 'testcontent')
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser2',
            'password': 'testpassword2'
        }), content_type='application/json')
        response = self.client.put(f'/api/users/{json.loads(login_response.data)["id"]}/notes/1', data=json.dumps({'content': 'newcontent'}), headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Forbidden')
        self.assertEqual(data['message'], 'Not authorized to access this resource')

    def test_update_note_different_user(self):
        self._create_test_user()
        self._create_test_user('testuser2', 'testpassword2')
        self._create_test_note(1, 'testcontent')
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser2',
            'password': 'testpassword2'
        }), content_type='application/json')
        response = self.client.put(f'/api/users/1/notes/1', data=json.dumps({'content': 'newcontent'}), headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Forbidden')
        self.assertEqual(data['message'], 'Not authorized to access this resource')

    def test_update_note_invalid_jwt(self):
        self._create_test_user()
        self._create_test_note(1, 'testcontent')
        self._create_test_user(username='tempuser', password='temppassword')
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'tempuser',
            'password': 'temppassword'
        }), content_type='application/json')
        self.client.delete(f'/api/users/{json.loads(login_response.data)["id"]}', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        response = self.client.put(f'/api/users/{json.loads(login_response.data)["id"]}/notes/1', data=json.dumps({'content': 'newcontent'}), headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Unauthorized')
        self.assertEqual(data['message'], 'User not found or JWT is invalid')

    def test_update_note_not_found(self):
        self._create_test_user()
        self._create_test_note(1, 'testcontent')
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        response = self.client.put(f'/api/users/{json.loads(login_response.data)["id"]}/notes/2', data=json.dumps({'content': 'newcontent'}), headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Note not found')
        self.assertEqual(data['message'], 'Note with id 2 does not exist in the database')

    def test_update_note_no_json(self):
        self._create_test_user()
        self._create_test_note(1, 'testcontent')
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        response = self.client.put(f'/api/users/{json.loads(login_response.data)["id"]}/notes/1', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Bad Request')
        self.assertEqual(data['message'], 'Could not load JSON from request')

    def test_delete_note(self):
        self._create_test_user()
        self._create_test_note(1, 'testcontent')
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        response = self.client.delete(f'/api/users/{json.loads(login_response.data)["id"]}/notes/1', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Note with id 1 successfully deleted')

    def test_delete_note_not_found(self):
        self._create_test_user()
        self._create_test_note(1, 'testcontent')
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        response = self.client.delete(f'/api/users/{json.loads(login_response.data)["id"]}/notes/2', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Note not found')
        self.assertEqual(data['message'], 'Note with id 2 does not exist in the database')

    def test_delete_note_invalid_jwt(self):
        self._create_test_user()
        self._create_test_note(1, 'testcontent')
        self._create_test_user(username='tempuser', password='temppassword')
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'tempuser',
            'password': 'temppassword'
        }), content_type='application/json')
        self.client.delete(f'/api/users/{json.loads(login_response.data)["id"]}', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'})
        response = self.client.delete(f'/api/users/{json.loads(login_response.data)["id"]}/notes/2', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Unauthorized')
        self.assertEqual(data['message'], 'User not found or JWT is invalid')

    def test_delete_note_different_owner(self):
        self._create_test_user()
        self._create_test_user('testuser2', 'testpassword2')
        self._create_test_note(1, 'testcontent')
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser2',
            'password': 'testpassword2'
        }), content_type='application/json')
        response = self.client.delete(f'/api/users/{json.loads(login_response.data)["id"]}/notes/1', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Forbidden')
        self.assertEqual(data['message'], 'Not authorized to access this resource')

    def test_delete_note_different_user(self):
        self._create_test_user()
        self._create_test_user('testuser2', 'testpassword2')
        self._create_test_note(1, 'testcontent')
        login_response = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser2',
            'password': 'testpassword2'
        }), content_type='application/json')
        response = self.client.delete(f'/api/users/1/notes/1', headers={'Authorization': f'Bearer {json.loads(login_response.data)["access_token"]}'}, content_type='application/json')
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Forbidden')
        self.assertEqual(data['message'], 'Not authorized to access this resource')

    def test_get_friends_notes(self):
        self._create_test_user()
        self._create_test_user('testuser2', 'testpassword2')
        login_response_1 = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        login_response_2 = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser2',
            'password': 'testpassword2'
        }), content_type='application/json')
        self.client.post(f'/api/users/{json.loads(login_response_1.data)["id"]}/notes', data=json.dumps({'content': 'testcontent'}), headers={'Authorization': f'Bearer {json.loads(login_response_1.data)["access_token"]}'}, content_type='application/json')
        self.client.post(f'/api/users/{json.loads(login_response_2.data)["id"]}/notes', data=json.dumps({'content': 'testcontent2'}), headers={'Authorization': f'Bearer {json.loads(login_response_2.data)["access_token"]}'}, content_type='application/json')
        response = self.client.post(f'/api/users/{json.loads(login_response_2.data)["id"]}/friends/{json.loads(login_response_1.data)["id"]}', headers={'Authorization': f'Bearer {json.loads(login_response_2.data)["access_token"]}'})
        response = self.client.get(f'/api/users/{json.loads(login_response_2.data)["id"]}/notes/friends', headers={'Authorization': f'Bearer {json.loads(login_response_1.data)["access_token"]}'})
        #print(response.data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], 2)
        self.assertEqual(data[0]['content'], 'testcontent2')

    def test_get_friends_notes_invalid_jwt(self):
        self._create_test_user()
        self._create_test_user('testuser2', 'testpassword2')
        login_response_1 = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        login_response_2 = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser2',
            'password': 'testpassword2'
        }), content_type='application/json')
        self.client.post(f'/api/users/{json.loads(login_response_1.data)["id"]}/notes', data=json.dumps({'user_id': '1', 'content': 'testcontent'}), headers={'Authorization': f'Bearer {json.loads(login_response_1.data)["access_token"]}'}, content_type='application/json')
        self.client.post(f'/api/users/{json.loads(login_response_2.data)["id"]}/notes', data=json.dumps({'user_id': '2', 'content': 'testcontent2'}), headers={'Authorization': f'Bearer {json.loads(login_response_2.data)["access_token"]}'}, content_type='application/json')
        response = self.client.post(f'/api/users/{json.loads(login_response_2.data)["id"]}/friends/{json.loads(login_response_1.data)["id"]}', headers={'Authorization': f'Bearer {json.loads(login_response_2.data)["access_token"]}'})
        self.client.delete(f'/api/users/{json.loads(login_response_1.data)["id"]}', headers={'Authorization': f'Bearer {json.loads(login_response_1.data)["access_token"]}'})
        response = self.client.get(f'/api/users/{json.loads(login_response_2.data)["id"]}/notes/friends', headers={'Authorization': f'Bearer {json.loads(login_response_1.data)["access_token"]}'})
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Unauthorized')
        self.assertEqual(data['message'], 'User not found or JWT is invalid')

    def test_get_friends_notes_different_user(self):
        self._create_test_user()
        self._create_test_user('testuser2', 'testpassword2')
        login_response_1 = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        login_response_2 = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser2',
            'password': 'testpassword2'
        }), content_type='application/json')
        self.client.post(f'/api/users/{json.loads(login_response_1.data)["id"]}/notes', data=json.dumps({'content': 'testcontent'}), headers={'Authorization': f'Bearer {json.loads(login_response_1.data)["access_token"]}'}, content_type='application/json')
        self.client.post(f'/api/users/{json.loads(login_response_2.data)["id"]}/notes', data=json.dumps({'content': 'testcontent2'}), headers={'Authorization': f'Bearer {json.loads(login_response_2.data)["access_token"]}'}, content_type='application/json')
        response = self.client.get(f'/api/users/{json.loads(login_response_2.data)["id"]}/notes/friends', headers={'Authorization': f'Bearer {json.loads(login_response_1.data)["access_token"]}'})
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Forbidden')
        self.assertEqual(data['message'], 'Not authorized to access this resource')

    def test_get_friends_notes_user_not_found(self):
        self._create_test_user()
        self._create_test_user('testuser2', 'testpassword2')
        login_response_1 = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        login_response_2 = self.client.post('/api/login', data=json.dumps({
            'username': 'testuser2',
            'password': 'testpassword2'
        }), content_type='application/json')
        self.client.post(f'/api/users/{json.loads(login_response_1.data)["id"]}/notes', data=json.dumps({'content': 'testcontent'}), headers={'Authorization': f'Bearer {json.loads(login_response_1.data)["access_token"]}'}, content_type='application/json')
        self.client.post(f'/api/users/{json.loads(login_response_2.data)["id"]}/notes', data=json.dumps({'content': 'testcontent2'}), headers={'Authorization': f'Bearer {json.loads(login_response_2.data)["access_token"]}'}, content_type='application/json')
        response = self.client.get(f'/api/users/100/notes/friends', headers={'Authorization': f'Bearer {json.loads(login_response_1.data)["access_token"]}'})
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'User Not Found')
        self.assertEqual(data['message'], 'User with id 100 does not exist in the database')
