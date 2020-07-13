# Generated by Django 3.0.7 on 2020-07-10 10:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    # replaces = [('massmeters', '0001_initial'), ('massmeters', '0002_auto_20200709_2359'), ('massmeters', '0003_auto_20200710_1329'), ('massmeters', '0004_auto_20200710_1343')]

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Crash',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dt_start', models.DateTimeField()),
                ('dt_stop', models.DateTimeField(blank=True, null=True)),
                ('text', models.TextField()),
                ('status', models.CharField(blank=True, max_length=200)),
                ('comment', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Поломка',
                'verbose_name_plural': 'Поломки',
            },
        ),
        migrations.CreateModel(
            name='MassMeter',
            fields=[
                ('name', models.CharField(blank=True, max_length=120)),
                ('execution', models.CharField(choices=[('FLR', 'Напольные'), ('CRN', 'Крановые')], default='FLR', max_length=3)),
                ('limit', models.FloatField()),
                ('measurement_error', models.FloatField()),
                ('sn', models.CharField(blank=True, max_length=50)),
                ('id', models.AutoField(auto_created=True, default=1, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Весы',
                'verbose_name_plural': 'Весы',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(default='')),
                ('code', models.CharField(choices=[('STR', 'Start'), ('MSG', 'Message'), ('FNS', 'Finish')], default='MSG', max_length=3)),
                ('dt_create', models.DateTimeField(auto_now_add=True)),
                ('crash_list', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='crash_messages', to='massmeters.Crash')),
                ('posted_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mass_meter_crash_message_posted_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Сообщение',
                'verbose_name_plural': 'Сообщения',
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object', models.CharField(max_length=120)),
                ('mass_object', models.FloatField()),
                ('mass_indication', models.FloatField()),
                ('dt_create', models.DateTimeField(auto_now_add=True)),
                ('posted_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('mass_meter', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mass_meter_events', to='massmeters.MassMeter')),
            ],
            options={
                'verbose_name': 'Взвешивание',
                'verbose_name_plural': 'Взвешивания',
            },
        ),
        migrations.AddField(
            model_name='crash',
            name='mass_meter',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mass_meter_crash', to='massmeters.MassMeter'),
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dt_create', models.DateTimeField(auto_now_add=True)),
                ('code', models.CharField(choices=[('DFL', 'Не установлены'), ('WRK', 'В рабочем состоянии'), ('TMF', 'Поверка просрочена'), ('LUP', 'Превышен предел погрешности'), ('FLS', 'Не исправны')], default='DFL', max_length=3)),
                ('mass_meter', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mass_meter_status', to='massmeters.MassMeter')),
            ],
            options={
                'verbose_name': 'Статус',
                'verbose_name_plural': 'Статусы',
            },
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=120)),
                ('date_create', models.DateField()),
                ('date_expiration', models.DateField()),
                ('mass_meter', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mass_meter_document', to='massmeters.MassMeter')),
                ('status', models.CharField(choices=[('DFL', 'Черновик'), ('ACL', 'Действующий'), ('HST', 'Архив')], default='DFL', max_length=3)),
            ],
            options={
                'verbose_name': 'Свидетельство о поверке',
                'verbose_name_plural': 'Свидетельства о поверке',
            },
        ),
    ]