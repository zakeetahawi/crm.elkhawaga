# Generated by Django 4.2.20 on 2025-04-15 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_auto_20250415_2017'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='نشط'),
        ),
    ]
