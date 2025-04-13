# Generated by Django 5.2 on 2025-04-13 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_companyinfo_formfield'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyinfo',
            name='description',
            field=models.TextField(blank=True, default='نظام متكامل لإدارة العملاء والمبيعات والإنتاج والمخزون', verbose_name='وصف الشركة'),
        ),
    ]
