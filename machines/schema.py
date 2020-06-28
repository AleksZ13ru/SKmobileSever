import graphene
from graphene_django import DjangoObjectType
from django.utils import timezone
from graphql_jwt.decorators import login_required

from .models import Location, Category, Machine, Value, Day, ToDoList, CrashList
from .type_scheme.stop_time_list_type import StopTimeListType, StopTimeList
from .type_scheme.todo_list_type import ToDoListType, ToDoList
from .type_scheme.crash_list_type import CrashListType, CrashList
from .type_scheme.service_name_type import ServiceNameType, ServiceName


class StatisticType(graphene.ObjectType):
    crash_in_work = graphene.Int()

    def resolve_crash_in_work(self, info, **kwargs):
        # service_id = kwargs.get('service_id')
        return CrashList.in_work()


class ValueType(DjangoObjectType):
    class Meta:
        model = Value

    speed = graphene.Int()
    kmv = graphene.Float()
    total_length = graphene.Float()

    def create_speed(self):
        return self.create_speed()

    def create_kmv(self):
        return self.create_kmv()

    def create_total_length(self):
        return self.create_total_length()

    def resolve_speed(self, info):
        return self.create_speed()

    def resolve_kmv(self, info):
        return self.create_kmv()

    def resolve_total_length(self, info):
        return self.create_total_length()


class DayType(DjangoObjectType):
    class Meta:
        model = Day
        # fields = ('id', 'day', '')

    total_stop_time_list_in_machine = graphene.Float(pk=graphene.Int())

    values_in_machine = graphene.List(ValueType, pk=graphene.Int())
    stop_time_lists_in_machine = graphene.List(StopTimeListType, pk=graphene.Int())
    todo_in_machine = graphene.List(ToDoListType, pk=graphene.Int())
    crash_list_in_machine = graphene.List(CrashListType, pk=graphene.Int())

    def resolve_values_in_machine(self, info, **kwargs):
        pk = kwargs.get('pk')
        return Value.objects.filter(machine_id=pk, day=self)

    def resolve_stop_time_lists_in_machine(self, info, **kwargs):
        pk = kwargs.get('pk')
        return StopTimeList.objects.filter(machine_id=pk, day_start=self)

    def resolve_total_stop_time_list_in_machine(self, info, **kwargs):
        pk = kwargs.get('pk')
        st = StopTimeList.objects.filter(machine_id=pk, day_start=self)
        result = 0
        for s in st:
            result = result + s.create_delta_time()
        return result

    def resolve_todo_in_machine(self, info, **kwargs):
        pk = kwargs.get('pk')
        # todo = ToDoList.objects.filter(machine_id=pk, day_start=self)
        # if todo is not None:
        #     return todo
        return ToDoList.objects.filter(machine_id=pk, day_start=self)

    def resolve_crash_list_in_machine(self, info, **kwargs):
        pk = kwargs.get('pk')
        # todo = ToDoList.objects.filter(machine_id=pk, day_start=self)
        # if todo is not None:
        #     return todo
        return CrashList.objects.filter(machine_id=pk, day_start=self)


class MachineType(DjangoObjectType):
    class Meta:
        model = Machine

    # speed = graphene.Int()
    kmv = graphene.Float()
    days = graphene.List(DayType)
    crash = graphene.Int()

    def resolve_days(self, info):
        result = Day.objects.all()
        return result

    # def create_speed(self):
    #     return self.create_speed()

    def create_kmv(self):
        return self.create_kmv()

    # def resolve_value(self, info, day):

    # return Value.objects.filter(day=day).first()
    # def resolve_speed(self, info):
    #     return self.create_speed()

    def resolve_kmv(self, info):
        return self.create_kmv()

    def create_crash(self):
        return self.create_crash()

    def resolve_crash(self, info):
        return self.create_crash()


class LocationType(DjangoObjectType):
    class Meta:
        model = Location


class CategoryType(DjangoObjectType):
    class Meta:
        model = Category


class CrashElementMutationAdd(graphene.Mutation):
    class Arguments:
        machine_id = graphene.Int()
        # dt_start = graphene.DateTime()
        services_id = graphene.List(graphene.Int)
        text = graphene.String()

    crash = graphene.Field(CrashListType)

    def mutate(self, info, machine_id, services_id, text):
        # {"machineId": 1, "dtStart": "2020-05-29T00:00:00Z", "servicesID": [1, 2], "text": "Hello"}
        # if dt_start is None:
        dt_start = timezone.now()
        day = Day.objects.get_or_create(day=dt_start.date())[0]

        services = []
        for service_id in services_id:
            service = ServiceName.objects.get(pk=service_id)
            services.append(service)

        crash = CrashList.objects.create(
            machine_id=machine_id,
            day_start=day,
            time_start=dt_start.time(),
            text=text
        )
        crash.services.set(services)
        # crash.text = text
        crash.save()
        return CrashElementMutationAdd(crash=crash)


class CrashElementMutationEdit(graphene.Mutation):
    class Arguments:
        crash_id = graphene.Int()
        finish = graphene.Boolean()
        text2 = graphene.String()

    crash = graphene.Field(CrashListType)

    def mutate(self, info, **kwargs):
        crash_id = kwargs.get('crash_id')
        finish = kwargs.get('finish')
        text2 = kwargs.get('text2')
        if finish:
            crash = CrashList.objects.get(pk=crash_id)
            dt_stop = timezone.now()
            day = Day.objects.get_or_create(day=dt_stop.date())[0]
            crash.day_stop = day
            crash.time_stop = dt_stop.time()
            crash.save()
            return CrashElementMutationEdit(crash=crash)
        return None


class AddStopTimeListMutation(graphene.Mutation):
    class Arguments:
        machine_id = graphene.Int()
        services_id = graphene.List(graphene.Int)
        dt_start = graphene.DateTime()
        dt_stop = graphene.DateTime()
        text = graphene.String()

    stop_time = graphene.Field(StopTimeListType)

    def mutate(self, info, machine_id, services_id, dt_start, dt_stop, text):
        # {"machineId": 1, "dtStart": "2020-05-29T00:00:00Z", "servicesID": [1, 2], "text": "Hello"}
        # if dt_start is None:
        # dt_start = timezone.now()
        day_start = Day.objects.get_or_create(day=dt_start.date())[0]
        day_stop = Day.objects.get_or_create(day=dt_stop.date())[0]

        services = []
        for service_id in services_id:
            service = ServiceName.objects.get(pk=service_id)
            services.append(service)

        stop_time = StopTimeList.objects.create(
            machine_id=machine_id,
            day_start=day_start,
            day_stop=day_stop,
            time_start=dt_start.time(),
            time_stop=dt_stop.time(),
            text=text
        )
        stop_time.services.set(services)
        # crash.text = text
        stop_time.save()
        return AddStopTimeListMutation(stop_time=stop_time)


class Query(object):
    days = graphene.List(DayType)
    locations = graphene.List(LocationType)
    category = graphene.List(CategoryType)
    machines = graphene.List(MachineType)
    machine = graphene.Field(MachineType, pk=graphene.Int())
    stop_time_list = graphene.Field(StopTimeListType, pk=graphene.Int())
    crash_element = graphene.Field(CrashListType, pk=graphene.Int())
    statistic = graphene.Field(StatisticType, service_id=graphene.Int(required=False))
    values = graphene.List(ValueType)

    # values_in_machine = graphene.List(ValueType, pk=graphene.Int())

    # stop_time_lists = graphene.List(StopTimeListType)

    @login_required
    def resolve_days(self, info, **kwargs):
        return Day.objects.all()

    @login_required
    def resolve_locations(self, info, **kwargs):
        return Location.objects.all()

    @login_required
    def resolve_category(self, info, **kwargs):
        return Category.objects.all()

    @login_required
    def resolve_machines(self, info, **kwargs):
        return Machine.objects.all()

    @login_required
    def resolve_machine(self, info, **kwargs):
        pk = kwargs.get('pk')
        return Machine.objects.get(pk=pk)

    @login_required
    def resolve_values(self, info, **kwargs):
        return Value.objects.all()

    # def resolve_values_in_machine(self, info, **kwargs):
    #     pk = kwargs.get('pk')
    #     return Value.objects.filter(machine_id=pk)

    @login_required
    def resolve_stop_time_lists(self, info, **kwargs):
        return StopTimeList.objects.all()

    @login_required
    def resolve_stop_time_list(self, info, **kwargs):
        pk = kwargs.get('pk')
        return StopTimeList.objects.get(pk=pk)

    @login_required
    def resolve_crash_element(self, info, **kwargs):
        pk = kwargs.get('pk')
        return CrashList.objects.get(pk=pk)

    @login_required
    def resolve_statistic(self, info, **kwargs):
        service_id = kwargs.get('service_id')
        return StatisticType()


class Mutation(graphene.ObjectType):
    crash_element_add = CrashElementMutationAdd.Field()
    crash_element_edit = CrashElementMutationEdit.Field()
    add_stop_time = AddStopTimeListMutation.Field()
