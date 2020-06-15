import graphene
from graphene_django import DjangoObjectType

from ..models import StopTimeList


class StopTimeListType(DjangoObjectType):
    class Meta:
        model = StopTimeList

    delta_time = graphene.Float()

    def create_delta_time(self):
        return self.create_delta_time()

    def resolve_delta_time(self, info, **kwargs):
        return self.create_delta_time()
