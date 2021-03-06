from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from subscribe.consumers import ChatSubscribe

DB_DATETIME_FORMAT = '%d/%b/%Y %H:%M:%S'
DB_DATE_FORMAT = '%d/%b/%Y'
DB_DATETIME_Z_FORMAT = '%m/%d/%Y 0:0'
DB_TIME_FORMAT = "%H:%M"


class Document(models.Model):
    class Meta:
        verbose_name = "Свидетельство о поверке"
        verbose_name_plural = "Свидетельства о поверке"

    class Status(models.TextChoices):
        DFL = 'DFL', _('Черновик')  # Default
        ACT = 'ACT', _('Действующее')  # Actual
        HST = 'HST', _('Архив')  # History

    mass_meter = models.ForeignKey('MassMeter', related_name='mass_meter_document', on_delete=models.CASCADE, null=True)
    number = models.CharField(max_length=120)
    date_create = models.DateField()  # дата создания
    date_expiration = models.DateField()  # дата окончания
    status = models.CharField(max_length=3, choices=Status.choices, default=Status.DFL)

    # file = models.FileField()

    def __str__(self):
        return "Свидетельство № %s до %s" % (self.number, self.date_expiration)


class Status(models.Model):
    class Meta:
        verbose_name = "Статус"
        verbose_name_plural = "Статусы"

    class Code(models.TextChoices):
        DFL = 'DFL', _('Не установлены')  # Default
        WRK = 'WRK', _('В рабочем состоянии')  # Work
        TMF = 'TMF', _('Поверка просрочена')  # Time Off
        LUP = 'LUP', _('Превышен предел погрешности')  # Limit Up
        FLS = 'FLS', _('Не исправны')  # False

    mass_meter = models.ForeignKey('MassMeter', related_name='mass_meter_status', on_delete=models.CASCADE, null=True)
    dt_create = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=3, choices=Code.choices, default=Code.DFL)

    def __str__(self):
        return "%s: %s" % (self.mass_meter, self.code)


class MassMeter(models.Model):
    class Meta:
        verbose_name = "Весы"
        verbose_name_plural = "Весы"

    class Execution(models.TextChoices):
        FLR = 'FLR', _('Напольные')  # Floor
        CRN = 'CRN', _('Крановые')  # Crane

    name = models.CharField(max_length=120, blank=True)
    sn = models.CharField(max_length=50, blank=True)
    execution = models.CharField(max_length=3, choices=Execution.choices, default=Execution.FLR)
    limit = models.FloatField()  # предел взвешивания
    measurement_error = models.FloatField()  # погрешность измерения

    def __str__(self):
        return "Весы %s (тип) до %.0f кг %s №%s" % (self.execution, self.limit, self.name, self.sn)


class Event(models.Model):
    class Meta:
        verbose_name = "Взвешивание"
        verbose_name_plural = "Взвешивания"

    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    mass_meter = models.ForeignKey('MassMeter', related_name='mass_meter_events', on_delete=models.CASCADE, null=True)
    object = models.CharField(
        max_length=120)  # нужно будет привязать каталог обектов взвешивания: Полуфабрикат, Тара, Контрольный груз
    mass_object = models.FloatField(null=True, blank=True)  # известный вес
    mass_indication = models.FloatField()  # показания весов
    dt_create = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s: %s - %.0f кг" % (self.mass_meter, self.object, self.mass_indication)


class Crash(models.Model):
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

    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='mass_meter_crash_message_posted_by',
                                  null=True, on_delete=models.CASCADE)
    crash_list = models.ForeignKey('Crash', related_name='crash_messages', on_delete=models.CASCADE, null=True)
    text = models.TextField(default='')
    code = models.CharField(max_length=3, choices=Code.choices, default=Code.MESSAGE)
    dt_create = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text


@receiver(post_save, sender=Event)
def event_save_callback(sender, **kwargs):
    room_name = 'mass_meter'
    message = {'massMeterLastUpdate': timezone.now().strftime("%m%d%Y%H%M%S")}
    ChatSubscribe.send_message(room_name=room_name, message=message)
