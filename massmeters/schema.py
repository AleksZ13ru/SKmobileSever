import graphene
from graphene_django import DjangoObjectType
from django.utils import timezone
from graphql_jwt.decorators import login_required

from .models import MassMeter, Document, Status, Event, Crash, Message


class DocumentType(DjangoObjectType):
    class Meta:
        model = Document


class StatusType(DjangoObjectType):
    class Meta:
        model = Status


class EventType(DjangoObjectType):
    class Meta:
        model = Event


class CrashType(DjangoObjectType):
    class Meta:
        model = Crash


class MassMeterType(DjangoObjectType):
    class Meta:
        model = MassMeter

    document_actual = graphene.Field(DocumentType)
    status_actual = graphene.Field(StatusType)
    events = graphene.List(EventType)
    accident = graphene.List(CrashType)

    def resolve_document_actual(self, info):
        return Document.objects.filter(mass_meter=self, status=Document.Status.ACT).first() or None

    def resolve_status_actual(self, info):
        return Status.objects.filter(mass_meter=self).last() or None

    def resolve_events(self, info):
        return Event.objects.filter(mass_meter=self) or None

    def resolve_accident(self, info):
        return Crash.objects.filter(mass_meter=self) or None


class CrashMutationAdd(graphene.Mutation):
    class Arguments:
        mass_meter_id = graphene.Int()
        text = graphene.String()

    crash = graphene.Field(CrashType)

    def mutate(self, info, mass_meter_id, text):
        user = info.context.user or None
        dt_start = timezone.now()

        crash = Crash.objects.create(
            mass_meter_id=mass_meter_id,
            dt_start=dt_start,
            text=text
        )

        crash.save()
        message = Message.objects.create(
            posted_by=user,
            crash_list=crash,
            text=text,
            code=Message.Code.START
        )
        message.save()
        return CrashMutationAdd(crash=crash)


class CrashMutationEdit(graphene.Mutation):
    class Arguments:
        crash_id = graphene.Int()
        finish = graphene.Boolean()
        # do_not_agree = graphene.Boolean()
        rewrite = graphene.Boolean()
        text = graphene.String()

    crash = graphene.Field(CrashType)

    def mutate(self, info, **kwargs):
        user = info.context.user or None
        crash_id = kwargs.get('crash_id')
        finish = kwargs.get('finish') or False
        rewrite = kwargs.get('rewrite') or False
        # do_not_agree = kwargs.get('do_not_agree') or False
        text = kwargs.get('text')
        crash = Crash.objects.get(pk=crash_id)
        message = Message.objects.create(
            posted_by=user,
            crash_list=crash,
            # do_not_agree=do_not_agree,
            text=text,
            code=Message.Code.MESSAGE
        )
        if finish:
            crash = Crash.objects.get(pk=crash_id)
            crash.dt_stop = timezone.now()
            message.code = Message.Code.FINISH
        if rewrite:
            crash.dt_stop = None
            message.code = Message.Code.START
        crash.save()
        message.save()
        return CrashMutationEdit(crash=crash)


class Query(object):
    mass_meters = graphene.List(MassMeterType)
    mass_meter = graphene.Field(MassMeterType, pk=graphene.Int())

    def resolve_mass_meters(self, info, **kwargs):
        return MassMeter.objects.all()

    def resolve_mass_meter(self, info, **kwargs):
        pk = kwargs.get('pk')
        return MassMeter.objects.get(pk=pk)


class Mutation(graphene.ObjectType):
    crash_add = CrashMutationAdd.Field()
    crash__edit = CrashMutationEdit.Field()
    event_add = AddStopTimeListMutation.Field()
