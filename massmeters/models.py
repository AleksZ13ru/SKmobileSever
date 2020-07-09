from django.db import models


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
    error = models.FloatField()  # погрешность
