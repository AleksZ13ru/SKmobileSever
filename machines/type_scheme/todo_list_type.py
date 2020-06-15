import graphene
from graphene_django import DjangoObjectType

from ..models import ToDoList


class ToDoListType(DjangoObjectType):
    class Meta:
        model = ToDoList
