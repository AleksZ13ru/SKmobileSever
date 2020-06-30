from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import datetime, date, time, timedelta
import json

DB_DATETIME_FORMAT = '%d/%b/%Y %H:%M:%S'
DB_DATE_FORMAT = '%d/%b/%Y'
DB_DATETIME_Z_FORMAT = '%m/%d/%Y 0:0'
DB_TIME_FORMAT = "%H:%M"


class ServiceName(models.Model):
    class Meta:
        verbose_name = "Сервисную службу"
        verbose_name_plural = "Службы"

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Day(models.Model):
    class Meta:
        verbose_name = "Дата"
        verbose_name_plural = "Даты"

    day = models.DateField()

    def __str__(self):
        return self.day.strftime(DB_DATE_FORMAT)


class Category(models.Model):
    class Meta:
        verbose_name = "Тип"
        verbose_name_plural = "Тип оборудования"

    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Location(models.Model):
    class Meta:
        verbose_name = "Участок"
        verbose_name_plural = "Участки"

    name = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return '{}'.format(self.name)


class Machine(models.Model):
    class Meta:
        verbose_name = "Оборудование"
        verbose_name_plural = "Оборудования"

    name = models.CharField(max_length=120, blank=True)
    comment = models.CharField(max_length=120, blank=True)
    category = models.ForeignKey('Category', related_name='machines', on_delete=models.CASCADE)
    location = models.ForeignKey('Location', related_name='machines', on_delete=models.CASCADE)

    def __str__(self):
        return '{}'.format(self.name)

    def create_kmv(self):
        value = Value.objects.filter(machine=self, day__day=timezone.datetime.now().date()).first()
        if value is not None:
            return value.create_kmv()
        return 0

    def create_crash(self):
        crash = CrashList.objects.filter(machine=self, day_stop=None)
        return len(crash)


class Value(models.Model):
    class Meta:
        verbose_name = "Значение"
        verbose_name_plural = "Значения"

    machine = models.ForeignKey('Machine', related_name='machine_value', on_delete=models.CASCADE)
    day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name='values_in_day')
    value = models.TextField(default='[]')
    status = models.TextField(default='[]')

    def __str__(self):
        result = '%s | %s=%d ' % (
            self.day.day.strftime(DB_DATE_FORMAT),
            self.machine,
            len(json.loads(self.value))
        )
        return result

    def create_kmv(self):
        values = json.loads(self.value)
        if len(values) > 0:
            return round((len(values) - values.count(0)) / len(values), 2)
        return 0

    def create_speed(self):
        length = 0
        work_time = 0
        speed = 0
        for s in json.loads(self.value):
            if s > 0:
                work_time = work_time + 1
                length = length + s
        if work_time != 0:
            speed = round(length / work_time, 2)
        return speed

    def create_total_length(self):
        length = 0
        for s in json.loads(self.value):
            length = length + s
        return length


class Message(models.Model):
    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

    class Code(models.TextChoices):
        START = 'STR', _('Start')
        MESSAGE = 'MSG', _('Message')
        FINISH = 'FNS', _('Finish')

    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    crash_list = models.ForeignKey('CrashList', related_name='crash_list_messages', on_delete=models.CASCADE, null=True)
    text = models.TextField(default='')
    code = models.CharField(max_length=3, choices=Code.choices, default=Code.MESSAGE)
    do_not_agree = models.BooleanField(default=False)  # не согласен с вызовом
    dt_create = models.DateTimeField(auto_now_add=True)


class CrashList(models.Model):
    # Вызов персонала на ремонт
    # todo: 1. Обработать ситуацию: вызваны 2 службы, причина поломки имеет отнашение к 1(или другой службе)
    class Meta:
        verbose_name = "Авария (вызов персонала)"
        verbose_name_plural = "Аварии (вызов персонала)"

    machine = models.ForeignKey('Machine', related_name='machine_crash_lists', on_delete=models.CASCADE)
    services = models.ManyToManyField(ServiceName, through='ServiceCrashList')
    day_start = models.ForeignKey(Day, on_delete=models.CASCADE, related_name='crash_list_in_day_start')
    day_stop = models.ForeignKey(Day, on_delete=models.CASCADE, blank=True, null=True)
    time_start = models.TimeField()
    time_stop = models.TimeField(blank=True, null=True)
    text = models.TextField()
    status = models.CharField(blank=True, max_length=200)
    comment = models.TextField(blank=True)


    def create_delta_time(self):
        d_start = date(self.day_start.day.year, self.day_start.day.month, self.day_start.day.day)
        t_start = time(self.time_start.hour, self.time_start.minute)
        dt_start = datetime.combine(d_start, t_start)
        if self.day_stop is None or self.time_stop is None:
            return 0
        else:
            d_stop = date(self.day_stop.day.year, self.day_stop.day.month, self.day_stop.day.day)
            t_stop = time(self.time_stop.hour, self.time_stop.minute)
            dt_stop = datetime.combine(d_stop, t_stop)
        return (dt_stop - dt_start).total_seconds() / 3600

    @staticmethod
    def in_work(service_id=None):
        if service_id is None:
            crash = CrashList.objects.filter(time_stop=None)
        else:
            crash = CrashList.objects.filter(time_stop=None, servicecrashlist__service_id=service_id)
        return len(crash)

    def __str__(self):
        day_stop = '?'
        if self.day_stop is not None:
            day_stop = self.day_stop.day.strftime(DB_DATE_FORMAT)
        result = '%s | %s --- %s | x часов' % (
            self.machine,
            self.day_start.day.strftime(DB_DATE_FORMAT),
            day_stop
        )
        return result


class ToDoList(models.Model):
    # Журнал передачи смен
    class Meta:
        verbose_name = "Выполненная работа (сменный журнал)"
        verbose_name_plural = "Выполненные работы (сменный журнал)"

    machine = models.ForeignKey('Machine', related_name='machine_todo_list', on_delete=models.CASCADE)
    services = models.ManyToManyField(ServiceName, through='ServiceToDoList', related_name='services_todo_list')
    day_start = models.ForeignKey(Day, on_delete=models.CASCADE, related_name='todo_list_in_day_start', default=None)
    day_stop = models.ForeignKey(Day, on_delete=models.CASCADE, blank=True, null=True)
    time_start = models.TimeField()
    time_stop = models.TimeField(blank=True, null=True)
    text = models.TextField()
    status = models.CharField(blank=True, max_length=200)
    comment = models.TextField(blank=True)

    def __str__(self):
        day_stop = '?'
        if self.day_stop is not None:
            day_stop = self.day_stop.day.strftime(DB_DATE_FORMAT)
        result = '%s | %s --- %s | x часов' % (
            self.machine,
            self.day_start.day.strftime(DB_DATE_FORMAT),
            day_stop
        )
        return result


class StopTimeList(models.Model):
    # Аварийное время простоя
    class Meta:
        verbose_name = "Простой оборудования"
        verbose_name_plural = "Ведомость простоев"

    def create_delta_time(self):
        d_start = date(self.day_start.day.year, self.day_start.day.month, self.day_start.day.day)
        t_start = time(self.time_start.hour, self.time_start.minute)
        dt_start = datetime.combine(d_start, t_start)
        if self.day_stop is None or self.time_stop is None:
            return 0
        else:
            d_stop = date(self.day_stop.day.year, self.day_stop.day.month, self.day_stop.day.day)
            t_stop = time(self.time_stop.hour, self.time_stop.minute)
            dt_stop = datetime.combine(d_stop, t_stop)
        return (dt_stop - dt_start).total_seconds() / 3600

    def __str__(self):
        day_stop = '?'
        # delta_time = 'x1'
        # d = date(self.day_start.day.year, self.day_start.day.month, self.day_start.day.day )
        # t = time(self.time_start.hour, self.time_start.minute)
        # t1 = time(self.time_stop.hour, self.time_stop.minute)
        # dt_start = datetime.combine(d, t)
        # dt_stop = datetime.combine(d, t1)
        # delta_time = dt_stop - dt_start
        if self.day_stop is not None:
            day_stop = self.day_stop.day.strftime(DB_DATE_FORMAT)
        result = '%s | %s --- %s | %s часов' % (
            self.machine,
            self.day_start.day.strftime(DB_DATE_FORMAT),
            day_stop,
            self.create_delta_time()

        )
        return result

    machine = models.ForeignKey('Machine', related_name='machine_stop_time_list', on_delete=models.CASCADE)
    services = models.ManyToManyField(ServiceName, through='ServiceStopTimeList',
                                      related_name='services_stop_time_list', )
    day_start = models.ForeignKey(Day, on_delete=models.CASCADE, related_name='stop_time_list_in_day_start')
    time_start = models.TimeField()
    # add_user =
    # work_user =
    # finish_user =
    # day_stop = models.ForeignKey(Day, on_delete=models.CASCADE, related_name='day_stop', blank=True, null=True)
    day_stop = models.ForeignKey(Day, on_delete=models.CASCADE, blank=True, null=True)
    time_stop = models.TimeField(blank=True, null=True)
    text = models.TextField()
    status = models.CharField(blank=True, max_length=200)
    comment = models.TextField(blank=True)


class ServiceStopTimeList(models.Model):
    stop_time_list = models.ForeignKey(StopTimeList, on_delete=models.CASCADE)
    service = models.ForeignKey(ServiceName, on_delete=models.CASCADE)


class ServiceToDoList(models.Model):
    todo_list = models.ForeignKey(ToDoList, on_delete=models.CASCADE)
    service = models.ForeignKey(ServiceName, on_delete=models.CASCADE)


class ServiceCrashList(models.Model):
    crash_list = models.ForeignKey(CrashList, on_delete=models.CASCADE)
    service = models.ForeignKey(ServiceName, on_delete=models.CASCADE)
