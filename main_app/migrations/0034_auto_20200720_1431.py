# Generated by Django 3.0.8 on 2020-07-20 14:31

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0033_auto_20200720_1430'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='tax_applied',
            field=models.DecimalField(blank=True, decimal_places=4, help_text="\n    Tax applied to orders (defaults to value tax value defined in user's profile)<br/>\n    • Leave this field blank to use the User's current discount ratio<br/>\n    • Must be a number from 0.00 to 1.00 (up to 2 decimal places)\n  ", max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
    ]
