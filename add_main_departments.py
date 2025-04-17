import django
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from accounts.models import Department

# الأقسام الأساسية للمشروع
main_departments = [
    {
        'name': 'العملاء',
        'code': 'customers',
        'description': 'قسم إدارة العملاء وكل ما يتعلق بهم',
        'icon': 'fa fa-users',
        'url_name': 'customers:dashboard',
        'order': 1,
    },
    {
        'name': 'الطلبات',
        'code': 'orders',
        'description': 'قسم إدارة الطلبات ومتابعتها',
        'icon': 'fa fa-shopping-cart',
        'url_name': 'orders:dashboard',
        'order': 2,
    },
    {
        'name': 'المعاينات',
        'code': 'inspections',
        'description': 'قسم المعاينات وجدولة زيارات العملاء',
        'icon': 'fa fa-search-location',
        'url_name': 'inspections:dashboard',
        'order': 3,
    },
    {
        'name': 'المصنع',
        'code': 'factory',
        'description': 'قسم التصنيع وتجهيز المنتجات',
        'icon': 'fa fa-industry',
        'url_name': 'factory:dashboard',
        'order': 4,
    },
    {
        'name': 'المخزون',
        'code': 'inventory',
        'description': 'قسم إدارة المخزون والمنتجات',
        'icon': 'fa fa-warehouse',
        'url_name': 'inventory:dashboard',
        'order': 5,
    },
    {
        'name': 'التقارير',
        'code': 'reports',
        'description': 'قسم التقارير والإحصائيات',
        'icon': 'fa fa-chart-bar',
        'url_name': 'reports:dashboard',
        'order': 6,
    },
    {
        'name': 'التركيبات',
        'code': 'installations',
        'description': 'قسم تركيب المنتجات للعملاء',
        'icon': 'fa fa-tools',
        'url_name': 'installations:dashboard',
        'order': 7,
    },
]


for dept in main_departments:
    obj, created = Department.objects.get_or_create(code=dept['code'], defaults=dept)
    if created:
        print(f"تم إنشاء القسم: {dept['name']}")
    else:
        print(f"القسم موجود مسبقًا: {dept['name']}")
