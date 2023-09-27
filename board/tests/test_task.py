from django.urls import reverse

from base_tests import BaseTestCase
from board.models import Board, Task


class TaskTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.board1 = Board.objects.create(
            owner=cls.users['user1']['obj'],
            name='board1'
        )
        cls.board2 = Board.objects.create(
            owner=cls.users['user2']['obj'],
            name='board2'
        )

    def test_create(self):
        data = {'title': '123'}
        path = reverse('task-list', kwargs={'board_pk': self.board1.id})

        self.switch_user('user1')

        response = self.client.post(path, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['creator']['id'], self.users['user1']['obj'].id)
        task_id = response.data['id']
        task = Task.objects.get(id=task_id)
        self.assertEqual(task.board, self.board1)

        self.switch_user('user2')

        response = self.client.post(path, data=data)
        self.assertEqual(response.status_code, 403)

    def test_list(self):
        pack_path = []
        data = {'title': '123'}

        for board_id in self.board1.id, self.board2.id:
            path_task_list = reverse('task-list', kwargs={'board_pk': board_id})
            path_board_detail = reverse('board-detail', kwargs={'pk': board_id})
            pack_path.append({
                'list': path_task_list,
                'detail': path_board_detail
            })

        def check_len_tasks(path, length):
            response = self.client.get(path['list'])
            self.assertEqual(len(response.data), length)
            response = self.client.get(path['detail'])
            self.assertEqual(len(response.data['tasks']), length)

        self.switch_user('user1')

        check_len_tasks(pack_path[0], 0)
        self.client.post(pack_path[0]['list'], data=data)
        check_len_tasks(pack_path[0], 1)

        self.switch_user('user2')

        check_len_tasks(pack_path[1], 0)
        self.client.post(pack_path[1]['list'], data=data)
        check_len_tasks(pack_path[1], 1)

        response = self.client.get(pack_path[1]['list'])
        self.assertEqual(
            tuple(response.data[0].keys()), ('id', 'is_close', 'title'),
            msg='Не те поля которые должны быть в task-list'
        )

    def create_task(self):
        data = {'title': '123'}
        path = reverse('task-list', kwargs={'board_pk': self.board1.id})

        self.switch_user('user1')

        response = self.client.post(path, data=data)
        return response.data['id']

    def test_detail(self):
        task_id = self.create_task()
        detail_path = reverse('task-detail', kwargs={'board_pk': self.board1.id, 'pk': task_id})
        response = self.client.get(detail_path)
        self.assertEqual(
            tuple(response.data.keys()), ('id', 'creator', 'is_close', 'title', 'content'),
            msg='Не те поля которые должны быть в task-detail'
        )

    def test_permission(self):
        task_id = self.create_task()
        path = reverse('task-detail', kwargs={'board_pk': self.board1.id, 'pk': task_id})

        response = self.client.patch(path, data={'title': '123'})
        self.assertEqual(response.status_code, 200)

        self.switch_user('user2')

        response = self.client.patch(path, data={'title': '123'})
        self.assertEqual(response.status_code, 403)

        response = self.client.delete(path)
        self.assertEqual(response.status_code, 403)

        self.switch_user('user1')

        response = self.client.delete(path)
        self.assertEqual(response.status_code, 204)

        response = self.client.get(path)
        self.assertEqual(response.status_code, 404)

    def test_close(self):
        task_id = self.create_task()
        path = reverse('task-close', kwargs={'board_pk': self.board1.id, 'pk': task_id})
        response = self.client.post(path)
        self.assertEqual(response.status_code, 204)
        task = Task.objects.get(id=task_id)
        self.assertEqual(task.is_close, True)
        response = self.client.post(path)
        self.assertEqual(response.status_code, 204)
        task = Task.objects.get(id=task_id)
        self.assertEqual(task.is_close, False)
