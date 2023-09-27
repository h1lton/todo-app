from django.urls import reverse

from base_tests import BaseTestCase


class BoardTests(BaseTestCase):
    def test_board_create(self):
        self.switch_user('user1')
        response = self.client.post(reverse('board-list'), data={'name': 'board1'})
        expected_json = {
            'owner': {'username': 'user1'},
            'users': [],
            'tasks': [],
            'name': 'board1'
        }
        self.assertEqual(expected_json['owner']['username'], response.data['owner']['username'])
        self.assertEqual(expected_json['name'], response.data['name'])
        self.assertEqual(expected_json['users'], response.data['users'])
        self.assertEqual(expected_json['tasks'], response.data['tasks'])
        self.assertEqual(len(response.data), 5)
        self.assertEqual(len(response.data['owner']), 2)

    def test_list(self):
        def check_len(length):
            response = self.client.get(reverse('board-list'))
            self.assertEqual(len(response.data), length)

        def create_board(user, num_board):
            self.switch_user(f'user{user}')
            check_len(num_board - 1)
            self.client.post(reverse('board-list'), data={'name': f'board{num_board}'})
            check_len(num_board)

        for i in range(1, 3):
            create_board(i, 1)
        create_board(1, 2)
        self.switch_user(f'user2')
        check_len(1)

    def test_read(self):
        self.switch_user('user1')

        response = self.client.post(reverse('board-list'), data={'name': 'board1'})
        path = reverse('board-detail', kwargs={'pk': response.data['id']})

        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)

        self.switch_user('user2')

        response = self.client.get(path)
        self.assertEqual(response.status_code, 404)

    def test_permission(self):
        self.switch_user('user1')

        response = self.client.post(reverse('board-list'), data={'name': 'board1'})
        path = reverse('board-detail', kwargs={'pk': response.data['id']})

        response = self.client.patch(path, data={'name': '123'})
        self.assertEqual(response.status_code, 200)

        self.switch_user('user2')

        response = self.client.patch(path, data={'name': '1'})
        self.assertEqual(response.status_code, 404)

        response = self.client.delete(path)
        self.assertEqual(response.status_code, 404)

        self.switch_user('user1')

        response = self.client.delete(path)
        self.assertEqual(response.status_code, 204)

        response = self.client.get(path)
        self.assertEqual(response.status_code, 404)
