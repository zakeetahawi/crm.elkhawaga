# Generated by Django 5.2 on 2025-04-09 16:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customers', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductionLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='اسم خط الإنتاج')),
                ('description', models.TextField(blank=True, verbose_name='الوصف')),
                ('is_active', models.BooleanField(default=True, verbose_name='نشط')),
            ],
            options={
                'verbose_name': 'خط إنتاج',
                'verbose_name_plural': 'خطوط الإنتاج',
            },
        ),
        migrations.CreateModel(
            name='ProductionOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'قيد الانتظار'), ('in_progress', 'جاري التصنيع'), ('quality_check', 'فحص الجودة'), ('completed', 'مكتمل'), ('cancelled', 'ملغي')], default='pending', max_length=20, verbose_name='الحالة')),
                ('start_date', models.DateTimeField(blank=True, null=True, verbose_name='تاريخ البدء')),
                ('end_date', models.DateTimeField(blank=True, null=True, verbose_name='تاريخ الانتهاء')),
                ('estimated_completion', models.DateTimeField(null=True, verbose_name='التاريخ المتوقع للانتهاء')),
                ('notes', models.TextField(blank=True, verbose_name='ملاحظات')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='production_orders_created', to=settings.AUTH_USER_MODEL, verbose_name='تم الإنشاء بواسطة')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='production_orders', to='customers.order', verbose_name='الطلب')),
                ('production_line', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='production_orders', to='factory.productionline', verbose_name='خط الإنتاج')),
            ],
            options={
                'verbose_name': 'أمر إنتاج',
                'verbose_name_plural': 'أوامر الإنتاج',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ProductionStage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='اسم المرحلة')),
                ('description', models.TextField(blank=True, verbose_name='الوصف')),
                ('start_date', models.DateTimeField(blank=True, null=True, verbose_name='تاريخ البدء')),
                ('end_date', models.DateTimeField(blank=True, null=True, verbose_name='تاريخ الانتهاء')),
                ('completed', models.BooleanField(default=False, verbose_name='مكتملة')),
                ('notes', models.TextField(blank=True, verbose_name='ملاحظات')),
                ('assigned_to', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_stages', to=settings.AUTH_USER_MODEL, verbose_name='تم التعيين إلى')),
                ('production_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stages', to='factory.productionorder', verbose_name='أمر الإنتاج')),
            ],
            options={
                'verbose_name': 'مرحلة إنتاج',
                'verbose_name_plural': 'مراحل الإنتاج',
                'ordering': ['start_date'],
            },
        ),
        migrations.CreateModel(
            name='QualityCheck',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('check_date', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الفحص')),
                ('result', models.CharField(choices=[('passed', 'ناجح'), ('failed', 'راسب'), ('needs_rework', 'يحتاج إعادة تصنيع')], max_length=20, verbose_name='النتيجة')),
                ('notes', models.TextField(blank=True, verbose_name='ملاحظات')),
                ('checked_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='quality_checks_performed', to=settings.AUTH_USER_MODEL, verbose_name='تم الفحص بواسطة')),
                ('production_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quality_checks', to='factory.productionorder', verbose_name='أمر الإنتاج')),
            ],
            options={
                'verbose_name': 'فحص جودة',
                'verbose_name_plural': 'فحوصات الجودة',
                'ordering': ['-check_date'],
            },
        ),
    ]
