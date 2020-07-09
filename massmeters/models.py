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


class Document(models.Model):
    class Meta:
        verbose_name = "Свидетельства о поверке"
        verbose_name_plural = "Свидетельства о поверке"

    number = models.CharField(max_length=120)
    date_create = models.DateField()  # дата создания
    date_expiration = models.DateField()  # дата окончания

    # file = models.FileField()

    def __str__(self):
        return "Свидетельство № %s до %s" % (self.number, self.date_expiration)


class Status(models.Model):
    class Code(models.TextChoices):
        DFL = 'FLR', _('Не установлены')  # Default
        WRK = 'CRN', _('В рабочем состоянии')  # Work
        TMF = 'FLR', _('Поверка просрочена')  # Time Off
        LUP = 'LUP', _('Превышен предел погрешности')  # Limit Up
        FLS = 'CRN', _('Не исправны')  # False

    mass_meter = models.ForeignKey('MassMeter', related_name='mass_meter_status', on_delete=models.CASCADE, null=True)
    dt_create = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=3, choices=Code.choices, default=Code.DFL)


class MassMeter(models.Model):
    class Meta:
        verbose_name = "Весы"
        verbose_name_plural = "Весы"

    class Type(models.TextChoices):
        FLR = 'FLR', _('Напольные')  # Floor
        CRN = 'CRN', _('Крановые')  # Crane

    name = models.CharField(max_length=120, blank=True)
    type = models.CharField(max_length=3, choices=Type.choices, default=Type.FLR)
    limit = models.FloatField()  # предел взвешивания
    measurement_error = models.FloatField()  # погрешность измерения
    document = models.OneToOneField(Document, on_delete=models.CASCADE, primary_key=True, )

    def __str__(self):
        return "Весы (тип) до %d - $s" % (self.limit, self.name)


class Event(models.Model):
    class Meta:
        verbose_name = "Взвешивание"
        verbose_name_plural = "Взвешивания"

    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    mass_meter = models.ForeignKey('MassMeter', related_name='mass_meter_events', on_delete=models.CASCADE, null=True)
    object = models.CharField(
        max_length=120)  # нужно будет привязать каталог обектов взвешивания: Полуфабрикат, Тара, Контрольный груз
    mass_object = models.FloatField()  # известный вес
    mass_indication = models.FloatField()  # показания весов
    dt_create = models.DateTimeField(auto_now_add=True)


class Crash(models.Model):
    # Вызов персонала на ремонт
    # todo: 1. Обработать ситуацию: вызваны 2 службы, причина поломки имеет отнашение к 1(или другой службе)
    class Meta:
        verbose_name = "Поломка"
        verbose_name_plural = "Поломки"

    mass_meter = models.ForeignKey('MassMeter', related_name='mass_meter_crash', on_delete=models.CASCADE, null=True)
    dt_start = models.DateTimeField()
    dt_stop = models.DateTimeField(blank=True, null=True)
    # time_start = models.TimeField()
    # time_stop = models.TimeField(blank=True, null=True)
    text = models.TextField()
    status = models.CharField(blank=True, max_length=200)  # reserve
    comment = models.TextField(blank=True)  # reserve

    def create_delta_time(self):
        if self.dt_stop is not None:
            return (self.dt_stop - self.dt_start).total_seconds() / 3600
        return 0

    @staticmethod
    def in_work():
        return len(Crash.objects.filter(dt_stop=None))

    def __str__(self):
        day_stop = '?'
        if self.dt_stop is not None:
            day_stop = self.dt_stop.strftime(DB_DATE_FORMAT)
        result = '%s | %s --- %s | x часов' % (
            self.mass_meter,
            self.dt_start.strftime(DB_DATE_FORMAT),
            day_stop
        )
        return result


class Message(models.Model):
    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

    class Code(models.TextChoices):
        START = 'STR', _('Start')
        MESSAGE = 'MSG', _('Message')
        FINISH = 'FNS', _('Finish')

    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    crash_list = models.ForeignKey('Crash', related_name='crash_messages', on_delete=models.CASCADE, null=True)
    text = models.TextField(default='')
    code = models.CharField(max_length=3, choices=Code.choices, default=Code.MESSAGE)
    dt_create = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
