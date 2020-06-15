import graphene
from graphene_django import DjangoObjectType

from ..models import ServiceName


class ServiceNameType(DjangoObjectType):
    class Meta:
        model = ServiceName
