# Generated by Django 3.2.25 on 2025-04-17 18:21

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('image', models.ImageField(blank=True, null=True, upload_to='users/', verbose_name='صورة المستخدم')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='رقم الهاتف')),
            ],
            options={
                'verbose_name': 'مستخدم',
                'verbose_name_plural': 'المستخدمين',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('address', models.TextField(blank=True, null=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('is_main_branch', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'فرع',
                'verbose_name_plural': 'الفروع',
            },
        ),
        migrations.CreateModel(
            name='CompanyInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.CharField(blank=True, default='', max_length=50, verbose_name='إصدار النظام')),
                ('release_date', models.CharField(blank=True, default='', max_length=50, verbose_name='تاريخ الإطلاق')),
                ('developer', models.CharField(blank=True, default='', max_length=100, verbose_name='المطور')),
                ('working_hours', models.CharField(blank=True, default='', max_length=100, verbose_name='ساعات العمل')),
                ('name', models.CharField(max_length=200)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='company_logos/')),
                ('address', models.TextField(blank=True, null=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('tax_number', models.CharField(blank=True, max_length=50, null=True)),
                ('commercial_register', models.CharField(blank=True, max_length=50, null=True)),
                ('website', models.URLField(blank=True, null=True)),
                ('social_links', models.JSONField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('facebook', models.URLField(blank=True, null=True)),
                ('twitter', models.URLField(blank=True, null=True)),
                ('instagram', models.URLField(blank=True, null=True)),
                ('linkedin', models.URLField(blank=True, null=True)),
                ('about', models.TextField(blank=True, null=True)),
                ('vision', models.TextField(blank=True, null=True)),
                ('mission', models.TextField(blank=True, null=True)),
                ('primary_color', models.CharField(blank=True, max_length=20, null=True)),
                ('secondary_color', models.CharField(blank=True, max_length=20, null=True)),
                ('accent_color', models.CharField(blank=True, max_length=20, null=True)),
            ],
            options={
                'verbose_name': 'معلومات الشركة',
                'verbose_name_plural': 'معلومات الشركة',
            },
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('code', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('icon', models.CharField(blank=True, help_text='Font Awesome icon name', max_length=50, null=True)),
                ('url_name', models.CharField(blank=True, max_length=100, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('order', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name': 'قسم',
                'verbose_name_plural': 'الأقسام',
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('priority', models.CharField(choices=[('low', 'منخفضة'), ('medium', 'متوسطة'), ('high', 'عالية')], default='medium', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('is_read', models.BooleanField(default=False)),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('read_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='read_notifications', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_notifications', to=settings.AUTH_USER_MODEL)),
                ('sender_department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sent_notifications', to='accounts.department')),
                ('target_branch', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.branch')),
                ('target_department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.department')),
                ('target_users', models.ManyToManyField(blank=True, related_name='received_notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'إشعار',
                'verbose_name_plural': 'الإشعارات',
                'ordering': ['-created_at'],
            },
        ),
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
        migrations.AddField(
            model_name='user',
            name='branch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users', to='accounts.branch', verbose_name='الفرع'),
        ),
        migrations.AddField(
            model_name='user',
            name='departments',
            field=models.ManyToManyField(blank=True, related_name='users', to='accounts.Department', verbose_name='الأقسام'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
