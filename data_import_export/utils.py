import os
import pandas as pd
import numpy as np
from django.utils.translation import gettext_lazy as _
from django.apps import apps
from django.utils import timezone
from django.db import transaction
from django.utils.text import slugify

def generate_multi_sheet_template(model_names):
    """
    Generate a multi-sheet Excel template for importing data
    
    Args:
        model_names: List of model names in the format 'app_label.model_name'
        
    Returns:
        BytesIO object containing the Excel file
    """
    import io
    
    # Create a BytesIO object to store the Excel file
    output = io.BytesIO()
    
    # Create a Pandas Excel writer using the BytesIO object
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # For each model, create a sheet with sample data
        for model_name in model_names:
            app_label, model = model_name.split('.')
            
            # Get the model class
            model_class = apps.get_model(app_label, model)
            
            # Get the field names
            fields = []
            for field in model_class._meta.fields:
                # Skip auto-generated fields
                if field.name in ['id', 'created_at', 'updated_at']:
                    continue
                
                # Skip file fields
                if field.get_internal_type() == 'FileField' or field.get_internal_type() == 'ImageField':
                    continue
                
                fields.append(field.name)
            
            # Create a sample dataframe
            sample_data = {}
            for field in fields:
                sample_data[field] = ['']
            
            df = pd.DataFrame(sample_data)
            
            # Write the dataframe to the Excel file
            df.to_excel(writer, sheet_name=model, index=False)
            
            # Get the worksheet
            worksheet = writer.sheets[model]
            
            # Add instructions as a header row
            instructions = f"قم بملء البيانات أدناه لاستيراد {model_class._meta.verbose_name_plural}"
            worksheet['A1'] = instructions
            
            # Add column descriptions as headers
            for i, field in enumerate(fields):
                field_obj = model_class._meta.get_field(field)
                description = str(field_obj.verbose_name)
                col_letter = chr(65 + i)  # A, B, C, etc.
                worksheet[f'{col_letter}2'] = description
    
    # Reset the pointer to the beginning of the BytesIO object
    output.seek(0)
    
    return output

def process_multi_sheet_import(file_path, import_log):
    """
    Process a multi-sheet Excel file for importing data
    
    Args:
        file_path: Path to the Excel file
        import_log: ImportExportLog instance
        
    Returns:
        Tuple of (success_count, error_count, error_details)
    """
    # Initialize counters
    total_success_count = 0
    total_error_count = 0
    error_details = []
    
    # Read the Excel file
    xls = pd.ExcelFile(file_path)
    
    # Process each sheet
    for sheet_name in xls.sheet_names:
        # Get the model name
        model_name = f"{import_log.model_name.split('.')[0]}.{sheet_name}"
        
        try:
            # Get the model class
            app_label, model = model_name.split('.')
            model_class = apps.get_model(app_label, model)
            
            # Read the sheet
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # Skip empty sheets
            if df.empty:
                continue
            
            # Process the data
            records_count = len(df)
            success_count = 0
            error_count = 0
            
            # Process each row
            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        # Skip empty rows
                        if row.isnull().all():
                            continue
                        
                        # Convert row to dict and remove NaN values
                        row_dict = {}
                        for key, value in row.to_dict().items():
                            if pd.notna(value):
                                row_dict[key] = value
                        
                        # Skip rows with no data
                        if not row_dict:
                            continue
                        
                        # Handle specific model import logic
                        if model == 'product':
                            # Handle product import
                            instance = handle_product_import(row_dict)
                        elif model == 'supplier':
                            # Handle supplier import
                            instance = handle_supplier_import(row_dict)
                        elif model == 'customer':
                            # Handle customer import
                            instance = handle_customer_import(row_dict)
                        elif model == 'order':
                            # Handle order import
                            instance = handle_order_import(row_dict)
                        else:
                            # Generic import
                            instance = model_class.objects.create(**row_dict)
                        
                        success_count += 1
                    except Exception as e:
                        error_count += 1
                        error_details.append(f"Sheet: {sheet_name}, Row {index+1}: {str(e)}")
            
            # Update counters
            total_success_count += success_count
            total_error_count += error_count
            
        except Exception as e:
            error_details.append(f"Sheet: {sheet_name}: {str(e)}")
    
    return total_success_count, total_error_count, error_details

def generate_multi_sheet_export(model_names):
    """
    Generate a multi-sheet Excel file for exporting data
    
    Args:
        model_names: List of model names in the format 'app_label.model_name'
        
    Returns:
        BytesIO object containing the Excel file
    """
    import io
    
    # Create a BytesIO object to store the Excel file
    output = io.BytesIO()
    
    # Create a Pandas Excel writer using the BytesIO object
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # For each model, create a sheet with data
        for model_name in model_names:
            app_label, model = model_name.split('.')
            
            # Get the model class
            model_class = apps.get_model(app_label, model)
            
            # Get all records
            queryset = model_class.objects.all()
            
            # Convert queryset to DataFrame
            data = []
            for obj in queryset:
                # Convert model instance to dict
                item = {}
                for field in model_class._meta.fields:
                    field_name = field.name
                    field_value = getattr(obj, field_name)
                    
                    # Handle foreign keys
                    if field.is_relation:
                        if field_value is not None:
                            field_value = str(field_value)
                        else:
                            field_value = None
                    
                    item[field_name] = field_value
                
                data.append(item)
            
            df = pd.DataFrame(data)
            
            # Write the dataframe to the Excel file
            df.to_excel(writer, sheet_name=model, index=False)
    
    # Reset the pointer to the beginning of the BytesIO object
    output.seek(0)
    
    return output

# Helper functions for importing specific models

def handle_product_import(data):
    """
    Handle product import
    """
    from inventory.models import Product, Category
    
    # Get or create category
    category = None
    if 'category' in data and data['category']:
        category, created = Category.objects.get_or_create(name=data['category'])
    
    # Create or update product
    if 'code' in data and data['code']:
        product, created = Product.objects.update_or_create(
            code=data['code'],
            defaults={
                'name': data.get('name', ''),
                'description': data.get('description', ''),
                'unit': data.get('unit', 'piece'),
                'price': data.get('price', 0),
                'minimum_stock': data.get('minimum_stock', 0),
                'category': category,
            }
        )
    else:
        product = Product.objects.create(
            name=data.get('name', ''),
            code=slugify(data.get('name', '')),
            description=data.get('description', ''),
            unit=data.get('unit', 'piece'),
            price=data.get('price', 0),
            minimum_stock=data.get('minimum_stock', 0),
            category=category,
        )
    
    return product

def handle_supplier_import(data):
    """
    Handle supplier import
    """
    from inventory.models import Supplier
    
    # Create or update supplier
    if 'name' in data and data['name']:
        supplier, created = Supplier.objects.update_or_create(
            name=data['name'],
            defaults={
                'contact_person': data.get('contact_person', ''),
                'phone': data.get('phone', ''),
                'email': data.get('email', ''),
                'address': data.get('address', ''),
                'tax_number': data.get('tax_number', ''),
                'notes': data.get('notes', ''),
            }
        )
    else:
        raise ValueError('Supplier name is required')
    
    return supplier

def handle_customer_import(data):
    """
    Handle customer import
    """
    from customers.models import Customer, CustomerCategory
    from accounts.models import Branch
    
    # Get or create category
    category = None
    if 'category' in data and data['category']:
        category, created = CustomerCategory.objects.get_or_create(name=data['category'])
    
    # Get branch
    branch = None
    if 'branch' in data and data['branch']:
        try:
            branch = Branch.objects.get(code=data['branch'])
        except Branch.DoesNotExist:
            branch = Branch.objects.first()
    else:
        branch = Branch.objects.first()
    
    # Create or update customer
    if 'code' in data and data['code']:
        customer, created = Customer.objects.update_or_create(
            code=data['code'],
            defaults={
                'name': data.get('name', ''),
                'phone': data.get('phone', ''),
                'email': data.get('email', ''),
                'address': data.get('address', ''),
                'customer_type': data.get('customer_type', 'individual'),
                'category': category,
                'branch': branch,
            }
        )
    else:
        customer = Customer.objects.create(
            name=data.get('name', ''),
            code=f"C{Customer.objects.count() + 1:04d}",
            phone=data.get('phone', ''),
            email=data.get('email', ''),
            address=data.get('address', ''),
            customer_type=data.get('customer_type', 'individual'),
            category=category,
            branch=branch,
        )
    
    return customer

def handle_order_import(data):
    """
    Handle order import
    """
    from orders.models import Order
    from customers.models import Customer
    from accounts.models import User
    
    # Get customer
    customer = None
    if 'customer' in data and data['customer']:
        try:
            customer = Customer.objects.get(name=data['customer'])
        except Customer.DoesNotExist:
            customer = Customer.objects.first()
    else:
        customer = Customer.objects.first()
    
    # Get user
    user = None
    if 'created_by' in data and data['created_by']:
        try:
            user = User.objects.get(username=data['created_by'])
        except User.DoesNotExist:
            user = User.objects.filter(is_staff=True).first()
    else:
        user = User.objects.filter(is_staff=True).first()
    
    # Create or update order
    if 'order_number' in data and data['order_number']:
        order, created = Order.objects.update_or_create(
            order_number=data['order_number'],
            defaults={
                'customer': customer,
                'delivery_date': data.get('delivery_date'),
                'status': data.get('status', 'pending'),
                'notes': data.get('notes', ''),
                'created_by': user,
            }
        )
    else:
        order = Order.objects.create(
            customer=customer,
            order_number=f"ORD{Order.objects.count() + 1:04d}",
            delivery_date=data.get('delivery_date'),
            status=data.get('status', 'pending'),
            notes=data.get('notes', ''),
            created_by=user,
        )
    
    return order
