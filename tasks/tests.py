from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import Task

import random
import string

used_strings = set()
characters = string.ascii_letters + string.digits


def generate_unique_random_string(length):
    while True:
        random_string = ''.join(random.choice(characters) for _ in range(length))
        if random_string not in used_strings:
            used_strings.add(random_string)
            return random_string


class TasksTests(APITestCase):
    def setUp(self) -> None:
        user1 = User.objects.create_user('user1')
        user2 = User.objects.create_user('user2')

        self.tokens = (
            Token.objects.create(user=user1),
            Token.objects.create(user=user2)
        )

        self.tasks = [
            Task.objects.create(user=user1, content='task user1'),
            Task.objects.create(user=user2, content='task user2')
        ]

    def test_task_list(self):
        """Видит ли user только свои задачи"""
        for i in range(2):
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.tokens[i].key)

            response = self.client.get(reverse('task-list'))
            self.assertEqual(response.json()[0].get('content'), f'task user{i + 1}')

            response = self.client.get(
                reverse('task-detail', kwargs={'pk': self.tasks[i].id})
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            response = self.client.get(
                reverse('task-detail', kwargs={'pk': self.tasks[i - 1].id})
            )
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_task(self):
        """Правильно ли определяется user для задачи"""
        for i in range(2):
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.tokens[i].key)
            data = {"content": generate_unique_random_string(5)}
            response = self.client.post(reverse('task-list'), data=data)

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            response = self.client.get(reverse('task-list'))
            self.assertEqual(response.json()[-1].get('content'), data['content'])

    def test_close_and_open_task(self):
        """Открытие и закрытие задачи"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.tokens[0].key)
        for i in range(2):
            response = self.client.post(reverse('task-close', kwargs={'pk': self.tasks[0].id}))

            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            self.tasks[0] = Task.objects.get(id=self.tasks[0].id)
            self.assertEqual(self.tasks[0].close, not bool(i))

    def test_close_and_open_someone_elses_task(self):
        """Запрет на открытие и закрытие чужой задачи"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.tokens[0].key)
        response = self.client.post(reverse('task-close', kwargs={'pk': self.tasks[1].id}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
