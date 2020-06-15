import graphene
from graphene_django import DjangoObjectType

from .models import Location, Category, Machine, Value, Day, ToDoList, CrashList
from .type_scheme.stop_time_list_type import StopTimeListType, StopTimeList
from .type_scheme.todo_list_type import ToDoListType, ToDoList
from .type_scheme.service_name_type import ServiceNameType, ServiceName


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

    values_in_machine = graphene.List(ValueType, pk=graphene.Int())
    stop_time_lists_in_machine = graphene.List(StopTimeListType, pk=graphene.Int())
    total_stop_time_list_in_machine = graphene.Float(pk=graphene.Int())
    todo_in_machine = graphene.List(ToDoListType, pk=graphene.Int())

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


class MachineType(DjangoObjectType):
    class Meta:
        model = Machine

    # speed = graphene.Int()
    kmv = graphene.Float()
    days = graphene.List(DayType)

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


class LocationType(DjangoObjectType):
    class Meta:
        model = Location


class CategoryType(DjangoObjectType):
    class Meta:
        model = Category


class Query(object):
    days = graphene.List(DayType)
    locations = graphene.List(LocationType)
    category = graphene.List(CategoryType)
    machines = graphene.List(MachineType)
    machine = graphene.Field(MachineType, pk=graphene.Int())
    stop_time_list = graphene.Field(StopTimeListType, pk=graphene.Int())
    values = graphene.List(ValueType)

    # values_in_machine = graphene.List(ValueType, pk=graphene.Int())

    # stop_time_lists = graphene.List(StopTimeListType)

    def resolve_days(self, info, **kwargs):
        return Day.objects.all()

    def resolve_locations(self, info, **kwargs):
        return Location.objects.all()

    def resolve_category(self, info, **kwargs):
        return Category.objects.all()

    def resolve_machines(self, info, **kwargs):
        return Machine.objects.all()

    def resolve_machine(self, info, **kwargs):
        pk = kwargs.get('pk')
        return Machine.objects.get(pk=pk)

    def resolve_values(self, info, **kwargs):
        return Value.objects.all()

    # def resolve_values_in_machine(self, info, **kwargs):
    #     pk = kwargs.get('pk')
    #     return Value.objects.filter(machine_id=pk)

    def resolve_stop_time_lists(self, info, **kwargs):
        return StopTimeList.objects.all()

    def resolve_stop_time_list(self, info, **kwargs):
        pk = kwargs.get('pk')
        return StopTimeList.objects.get(pk=pk)
