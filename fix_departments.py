import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from accounts.models import Department

# الأقسام الصحيحة وurl_name لكل قسم
correct_departments = [
    {'code': 'customers', 'name': 'العملاء', 'url_name': 'customers:customer_list'},
    {'code': 'orders', 'name': 'الطلبات', 'url_name': 'orders:order_list'},
    {'code': 'inspections', 'name': 'المعاينات', 'url_name': 'inspections:dashboard'},
    {'code': 'factory', 'name': 'المصنع', 'url_name': 'factory:factory_list'},
    {'code': 'inventory', 'name': 'المخزون', 'url_name': 'inventory:inventory_list'},
    {'code': 'reports', 'name': 'التقارير', 'url_name': 'reports:report_list'},
    {'code': 'installations', 'name': 'التركيبات', 'url_name': 'installations:installation_list'},
]


# حذف أي قسم غير صحيح (ليس من القائمة)
Department.objects.exclude(code__in=[d['code'] for d in correct_departments]).delete()

# تحديث أو إنشاء الأقسام الصحيحة
for dept in correct_departments:
    obj, created = Department.objects.update_or_create(
        code=dept['code'],
        defaults={
            'name': dept['name'],
            'url_name': dept['url_name'],
            'is_active': True
        }
    )
    if created:
        print(f"تم إنشاء القسم: {dept['name']}")
    else:
        print(f"تم تحديث القسم: {dept['name']}")
