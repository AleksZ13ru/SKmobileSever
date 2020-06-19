from django.contrib import admin
from .models import Category, Location, Machine, Value, StopTimeList, ToDoList, CrashList, ServiceName, \
    ServiceStopTimeList, ServiceToDoList, Day, ServiceCrashList


class ServiceStopTimeListInline(admin.TabularInline):
    model = ServiceStopTimeList
    extra = 2


class ServiceToDoListInline(admin.TabularInline):
    model = ServiceToDoList
    extra = 2


class ServiceCrashListInline(admin.TabularInline):
    model = ServiceCrashList
    extra = 2


class StopTimeListAdmin(admin.ModelAdmin):
    inlines = (ServiceStopTimeListInline,)


class ToDoListAdmin(admin.ModelAdmin):
    inlines = (ServiceToDoListInline,)


class CrashListAdmin(admin.ModelAdmin):
    inlines = (ServiceCrashListInline,)


class StopTimeListInline(admin.TabularInline):
    model = StopTimeList
    extra = 2


class DayAdmin(admin.ModelAdmin):
    pass
    # inlines = (StopTimeListInline,)


admin.site.register(Location)
admin.site.register(Category)
admin.site.register(Machine)
admin.site.register(Value)
admin.site.register(Day, DayAdmin)
admin.site.register(StopTimeList, StopTimeListAdmin)
admin.site.register(ServiceStopTimeList)
admin.site.register(ToDoList, ToDoListAdmin)
admin.site.register(CrashList, CrashListAdmin)
admin.site.register(ServiceName)
