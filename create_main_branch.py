import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

# Import models
from accounts.models import Branch

# Create main branch if it doesn't exist
if not Branch.objects.filter(is_main_branch=True).exists():
    Branch.objects.create(
        code='001',
        name='الفرع الرئيسي',
        address='العنوان الرئيسي',
        phone='123456789',
        is_main_branch=True
    )
    print("Main branch created successfully.")
else:
    print("Main branch already exists.")
