# Generated by Django 3.0.8 on 2020-10-03 04:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0060_auto_20201002_1937'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartdetail',
            name='date_relevant',
        ),
    ]
