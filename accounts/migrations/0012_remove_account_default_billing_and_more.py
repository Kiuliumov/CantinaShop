# Generated by Django 5.2.4 on 2025-07-25 05:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_account_country_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='default_billing',
        ),
        migrations.RemoveField(
            model_name='address',
            name='address_type',
        ),
        migrations.RemoveField(
            model_name='address',
            name='is_default',
        ),
    ]
