import graphene
from graphene_django import DjangoObjectType

from ..models import CrashList


class CrashListType(DjangoObjectType):
    class Meta:
        model = CrashList
