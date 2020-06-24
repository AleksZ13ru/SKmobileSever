import graphene
from graphene_django import DjangoObjectType

from ..models import CrashList


class CrashListType(DjangoObjectType):
    class Meta:
        model = CrashList

    delta_time = graphene.Float()
    in_work = graphene.Int()

    def create_delta_time(self):
        return self.create_delta_time()

    def resolve_delta_time(self, info, **kwargs):
        return self.create_delta_time()

    @staticmethod
    def resolve_in_work(self, info, **kwargs):
        return CrashList.create_in_work()
