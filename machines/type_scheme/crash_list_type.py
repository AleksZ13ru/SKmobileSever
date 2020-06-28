import graphene
from graphene_django import DjangoObjectType

from ..models import CrashList
from .crash_list_message_type import MessageType, Message


class CrashListType(DjangoObjectType):
    class Meta:
        model = CrashList

    delta_time = graphene.Float()
    in_work = graphene.Int()
    messages = graphene.List(MessageType)

    def create_delta_time(self):
        return self.create_delta_time()

    def resolve_delta_time(self, info, **kwargs):
        return self.create_delta_time()

    def resolve_messages(self, info, **kwargs):
        crash_list_pk = kwargs.get('pk')
        return Message.objects.filter(crash_list=self)

    @staticmethod
    def resolve_in_work(self, info, **kwargs):
        return CrashList.create_in_work()
