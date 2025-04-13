#!/usr/bin/env python
"""
Script to test the system's functionality from order creation to inventory notification.
This script creates sample data to test the workflow from order creation to production and inventory.
"""

import os
import sys
import django
import random
from datetime import datetime, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

# Import models after Django setup
from django.contrib.auth import get_user_model
from accounts.models import Branch, Department
from customers.models import Customer, CustomerCategory
from inventory.models import Product, Category, StockTransaction
from orders.models import Order, OrderItem
from orders.extended_models import ExtendedOrder
from factory.models import ProductionLine, ProductionStage, ProductionOrder, ProductionIssue
from inspections.models import Inspection, InspectionReport
from accounts.models import Notification

User = get_user_model()

def create_test_workflow():
    """Create a complete test workflow from order to production and inventory"""
    print("Starting test workflow creation...")
    
    # Get or create admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'is_staff': True,
            'is_superuser': True,
            'email': 'admin@example.com',
        }
    )
    if created:
        admin_user.set_password('admin')
        admin_user.save()
        print("Created admin user")
    
    # Get or create main branch
    main_branch, created = Branch.objects.get_or_create(
        code='001',
        defaults={
            'name': 'الفرع الرئيسي',
            'address': 'القاهرة',
            'phone': '01234567890',
            'is_main_branch': True,
        }
    )
    if created:
        print("Created main branch")
    
    # Assign branch to admin user if not assigned
    if not admin_user.branch:
        admin_user.branch = main_branch
        admin_user.save()
        print("Assigned main branch to admin user")
    
    # Get or create customer category
    category, created = CustomerCategory.objects.get_or_create(
        name='عميل عادي',
        defaults={
            'description': 'فئة العملاء العاديين',
        }
    )
    if created:
        print("Created customer category")
    
    # Get or create customer
    customer, created = Customer.objects.get_or_create(
        name='عميل اختبار',
        defaults={
            'phone': '01234567890',
            'email': 'test@example.com',
            'address': 'القاهرة',
            'branch': main_branch,
            'customer_type': 'individual',
            'category': category,
        }
    )
    if created:
        print("Created test customer")
    
    # Get or create product category
    product_category, created = Category.objects.get_or_create(
        name='منتجات اختبار',
        defaults={
            'description': 'فئة منتجات الاختبار',
        }
    )
    if created:
        print("Created product category")
    
    # Get or create products
    products = []
    for i in range(1, 4):
        product, created = Product.objects.get_or_create(
            code=f'TEST{i:03d}',
            defaults={
                'name': f'منتج اختبار {i}',
                'category': product_category,
                'description': f'وصف منتج اختبار {i}',
                'unit': 'piece',
                'price': random.randint(100, 1000),
                'minimum_stock': 5,
            }
        )
        if created:
            # Add initial stock
            StockTransaction.objects.create(
                product=product,
                transaction_type='in',
                reason='initial',
                quantity=random.randint(10, 20),
                created_by=admin_user,
            )
            print(f"Created product {product.name} with initial stock")
        products.append(product)
    
    # Create order
    order = Order.objects.create(
        customer=customer,
        order_number=f'ORD-{datetime.now().strftime("%Y%m%d")}-{random.randint(1000, 9999)}',
        status='pending',
        created_by=admin_user,
    )
    print(f"Created order {order.order_number}")
    
    # Create extended order
    extended_order = ExtendedOrder.objects.create(
        order=order,
        order_type='product',
        goods_type='furniture',
        branch=main_branch,
    )
    print("Created extended order details")
    
    # Add order items
    for product in products:
        quantity = random.randint(1, 3)
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            unit_price=product.price,
        )
        print(f"Added {quantity} of {product.name} to order")
    
    # Create production line
    production_line, created = ProductionLine.objects.get_or_create(
        name='خط إنتاج اختبار',
        defaults={
            'description': 'خط إنتاج للاختبار',
            'is_active': True,
        }
    )
    if created:
        print("Created production line")
    
    # Define production stage names
    stage_names = ['تجهيز', 'قص', 'تجميع', 'دهان', 'تشطيب']
    
    # Create production order
    production_order = ProductionOrder.objects.create(
        order=order,
        production_line=production_line,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=7),
        status='in_progress',
        created_by=admin_user,
    )
    print(f"Created production order for order {order.order_number}")
    
    # Create production stages for the order
    for i, name in enumerate(stage_names):
        production_stage = ProductionStage.objects.create(
            production_order=production_order,
            name=name,
            description=f'مرحلة {name}',
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(hours=random.randint(1, 24)),
            completed=True,
            notes=f'تم إكمال مرحلة {name} بنجاح',
            assigned_to=admin_user,
        )
        print(f"Created production stage: {production_stage.name} for the order")
    
    # Create inspection
    inspection = Inspection.objects.create(
        customer=customer,
        contract_number=f'INSP-{datetime.now().strftime("%Y%m%d")}-{random.randint(1000, 9999)}',
        request_date=datetime.now().date(),
        scheduled_date=(datetime.now() + timedelta(days=1)).date(),
        status='pending',
        notes='معاينة للاختبار',
        created_by=admin_user,
        branch=main_branch,
    )
    print("Created inspection")
    
    # Create inspection report
    report = InspectionReport.objects.create(
        title=f'تقرير معاينة {inspection.id}',
        report_type='custom',
        branch=main_branch,
        date_from=datetime.now().date(),
        date_to=(datetime.now() + timedelta(days=30)).date(),
        notes='محتوى تقرير المعاينة للاختبار',
        created_by=admin_user,
    )
    print("Created inspection report")
    
    # Create notifications
    departments = Department.objects.all()
    if departments.exists():
        factory_dept = departments.filter(code='factory').first() or departments.first()
        inventory_dept = departments.filter(code='inventory').first() or departments.first()
        
        # Notification for production
        Notification.objects.create(
            title='طلب إنتاج جديد',
            message=f'تم إنشاء طلب إنتاج جديد للطلب رقم {order.order_number}',
            priority='high',
            sender=admin_user,
            sender_department=factory_dept,
            target_department=factory_dept,
            target_branch=main_branch,
        )
        print("Created production notification")
        
        # Notification for inventory
        Notification.objects.create(
            title='طلب سحب من المخزون',
            message=f'يرجى تجهيز المواد الخام للطلب رقم {order.order_number}',
            priority='medium',
            sender=admin_user,
            sender_department=factory_dept,
            target_department=inventory_dept,
            target_branch=main_branch,
        )
        print("Created inventory notification")
    
    print("\nTest workflow created successfully!")
    print(f"Order Number: {order.order_number}")
    print(f"Production Order ID: {production_order.id}")
    print(f"Inspection ID: {inspection.id}")
    print("\nYou can now log in with username 'admin' and password 'admin' to view the created data.")

if __name__ == '__main__':
    create_test_workflow()
