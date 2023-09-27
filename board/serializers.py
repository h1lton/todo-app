from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Board, Task


class ListBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ('id', 'name')


class UserSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()

    class Meta:
        ref_name = 'board user'
        model = User
        fields = ('id', 'username')


class BoardDefault:
    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context['view'].kwargs['board_pk']

    def __repr__(self):
        return '%s()' % self.__class__.__name__


class ListTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'is_close', 'title')


class DetailTaskSerializer(serializers.ModelSerializer):
    board = serializers.HiddenField(source='board_id', default=BoardDefault())
    hidden_creator = serializers.HiddenField(source='creator', default=serializers.CurrentUserDefault())
    creator = UserSerializer(read_only=True)
    is_close = serializers.ReadOnlyField()

    class Meta:
        model = Task
        fields = '__all__'


class DetailBoardSerializer(serializers.ModelSerializer):
    hidden_owner = serializers.HiddenField(source='owner', default=serializers.CurrentUserDefault())
    owner = UserSerializer(read_only=True)
    users = UserSerializer(many=True, read_only=True)
    tasks = ListTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = '__all__'
