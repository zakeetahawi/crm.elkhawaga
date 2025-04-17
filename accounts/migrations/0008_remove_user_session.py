from django.db import migrations, models
import django.db.models.deletion
from django.contrib.auth import get_user_model


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_companyinfo_description'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='FormField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('form_type', models.CharField(choices=[('customer', 'نموذج العميل'), ('order', 'نموذج الطلب'), ('inspection', 'نموذج المعاينة'), ('installation', 'نموذج التركيب'), ('product', 'نموذج المنتج')], max_length=20)),
                ('field_name', models.CharField(max_length=100)),
                ('field_label', models.CharField(max_length=200)),
                ('field_type', models.CharField(choices=[('text', 'نص'), ('number', 'رقم'), ('email', 'بريد إلكتروني'), ('phone', 'هاتف'), ('date', 'تاريخ'), ('select', 'قائمة اختيار'), ('checkbox', 'مربع اختيار'), ('radio', 'زر اختيار'), ('textarea', 'منطقة نص'), ('file', 'ملف')], max_length=20)),
                ('required', models.BooleanField(default=False)),
                ('enabled', models.BooleanField(default=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('choices', models.TextField(blank=True, help_text='قائمة الخيارات مفصولة بفواصل (للحقول من نوع select, radio, checkbox)', null=True)),
                ('default_value', models.CharField(blank=True, max_length=255, null=True)),
                ('help_text', models.CharField(blank=True, max_length=255, null=True)),
                ('min_length', models.PositiveIntegerField(blank=True, null=True)),
                ('max_length', models.PositiveIntegerField(blank=True, null=True)),
                ('min_value', models.FloatField(blank=True, null=True)),
                ('max_value', models.FloatField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'حقل نموذج',
                'verbose_name_plural': 'حقول النماذج',
                'unique_together': {('form_type', 'field_name')},
            },
        ),
    ]
