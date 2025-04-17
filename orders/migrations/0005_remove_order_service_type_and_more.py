# Generated by Django 4.2.20 on 2025-04-15 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_remove_order_delivery_date_remove_order_goods_type_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='service_type',
        ),
        migrations.AddField(
            model_name='order',
            name='last_notification_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='تاريخ آخر إشعار'),
        ),
        migrations.AddField(
            model_name='order',
            name='service_types',
            field=models.JSONField(blank=True, default=list, verbose_name='أنواع الخدمات'),
        ),
        migrations.AddField(
            model_name='order',
            name='tracking_status',
            field=models.CharField(choices=[('pending', 'قيد الانتظار'), ('processing', 'قيد المعالجة'), ('warehouse', 'في المستودع'), ('factory', 'في المصنع'), ('cutting', 'قيد القص'), ('ready', 'جاهز للتسليم'), ('delivered', 'تم التسليم')], default='pending', max_length=20, verbose_name='حالة التتبع'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='item_type',
            field=models.CharField(choices=[('fabric', 'قماش'), ('accessory', 'إكسسوار')], default='fabric', max_length=10, verbose_name='نوع العنصر'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='processing_status',
            field=models.CharField(choices=[('pending', 'قيد الانتظار'), ('processing', 'قيد المعالجة'), ('warehouse', 'في المستودع'), ('factory', 'في المصنع'), ('cutting', 'قيد القص'), ('ready', 'جاهز للتسليم'), ('delivered', 'تم التسليم')], default='pending', max_length=20, verbose_name='حالة المعالجة'),
        ),
    ]
