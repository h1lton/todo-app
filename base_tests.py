from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class BaseTestCase(APITestCase):
    users = dict()

    @classmethod
    def create_user(cls, username, password=None, email=None):
        user = User.objects.create_user(username, password=password, email=email)
        token_user = Token.objects.create(user=user)
        cls.users[username] = {
            'obj': user,
            'token': token_user.key
        }

    def switch_user(self, username):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.users[username]['token'])

    @classmethod
    def create_default_stack_users(cls):
        for username in ['admin', 'user1', 'user2']:
            cls.create_user(username)

    @classmethod
    def setUpTestData(cls):
        cls.create_default_stack_users()
