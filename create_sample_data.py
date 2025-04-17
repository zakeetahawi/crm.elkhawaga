import pandas as pd
import os
from datetime import datetime, timedelta
import random

# Crear directorio para los archivos de datos si no existe
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data_files')
os.makedirs(data_dir, exist_ok=True)

# Ruta del archivo Excel
excel_file = os.path.join(data_dir, 'sample_data.xlsx')

# Crear un escritor de Excel
writer = pd.ExcelWriter(excel_file, engine='openpyxl')

# 1. Datos de muestra para Categorías de Productos
categories = [
    {'name': 'قماش', 'description': 'أنواع مختلفة من الأقمشة'},
    {'name': 'ستارة خفيف', 'description': 'ستائر خفيفة للنوافذ'},
    {'name': 'ستارة ثقيل', 'description': 'ستائر ثقيلة للنوافذ الكبيرة'},
    {'name': 'إكسسوار', 'description': 'إكسسوارات للستائر والمفروشات'},
    {'name': 'مفروشات', 'description': 'مفروشات متنوعة للمنازل'},
]
df_categories = pd.DataFrame(categories)
df_categories.to_excel(writer, sheet_name='Categories', index=False)

# 2. Datos de muestra para Productos
products = []
for i in range(1, 31):
    category = random.choice(categories)['name']
    unit_choices = ['piece', 'meter', 'sqm', 'kg']
    product = {
        'name': f'منتج {i}',
        'code': f'PROD{i:03d}',
        'category': category,
        'description': f'وصف للمنتج رقم {i}',
        'unit': random.choice(unit_choices),
        'price': round(random.uniform(50, 5000), 2),
        'cost_price': round(random.uniform(30, 3000), 2),
        'minimum_stock': random.randint(5, 20),
        'current_stock': random.randint(0, 50),
        'is_active': True
    }
    products.append(product)

df_products = pd.DataFrame(products)
df_products.to_excel(writer, sheet_name='Products', index=False)

# 3. Datos de muestra para Proveedores
suppliers = []
for i in range(1, 11):
    supplier = {
        'name': f'مورد {i}',
        'contact_person': f'شخص الاتصال {i}',
        'phone': f'01{random.randint(10000000, 99999999)}',
        'email': f'supplier{i}@example.com',
        'address': f'عنوان المورد {i}، القاهرة',
        'tax_number': f'TAX{i:05d}',
        'notes': f'ملاحظات عن المورد {i}'
    }
    suppliers.append(supplier)

df_suppliers = pd.DataFrame(suppliers)
df_suppliers.to_excel(writer, sheet_name='Suppliers', index=False)

# 4. Datos de muestra para Categorías de Clientes
customer_categories = [
    {'name': 'عميل عادي', 'description': 'عملاء التجزئة العاديين'},
    {'name': 'عميل مميز', 'description': 'عملاء مميزين بمشتريات متكررة'},
    {'name': 'عميل VIP', 'description': 'عملاء كبار بمشتريات عالية القيمة'},
    {'name': 'شركة', 'description': 'عملاء من الشركات'},
    {'name': 'مصمم', 'description': 'مصممي الديكور والمفروشات'},
]
df_customer_categories = pd.DataFrame(customer_categories)
df_customer_categories.to_excel(writer, sheet_name='CustomerCategories', index=False)

# 5. Datos de muestra para Clientes
customers = []
for i in range(1, 51):
    customer_type = random.choice(['retail', 'wholesale', 'corporate'])
    category = random.choice(customer_categories)['name']
    customer = {
        'code': f'CUST{i:03d}',
        'name': f'عميل {i}',
        'customer_type': customer_type,
        'category': category,
        'phone': f'01{random.randint(10000000, 99999999)}',
        'email': f'customer{i}@example.com',
        'address': f'عنوان العميل {i}، القاهرة',
        'status': 'active',
        'branch': 'الفرع الرئيسي',  # Asegúrate de que este valor exista en tu sistema
        'notes': f'ملاحظات عن العميل {i}'
    }
    customers.append(customer)

df_customers = pd.DataFrame(customers)
df_customers.to_excel(writer, sheet_name='Customers', index=False)

# 6. Datos de muestra para Pedidos
orders = []
order_items = []

for i in range(1, 31):
    customer = random.choice(customers)
    order_date = datetime.now() - timedelta(days=random.randint(0, 90))
    delivery_type = random.choice(['home', 'branch'])
    status = random.choice(['normal', 'vip'])
    tracking_status = random.choice(['pending', 'processing', 'warehouse', 'factory', 'cutting', 'ready', 'delivered'])
    
    # Calcular valores totales
    total_amount = 0
    paid_amount = 0
    
    order = {
        'order_number': f'ORD{i:05d}',
        'customer': customer['name'],
        'customer_code': customer['code'],
        'order_date': order_date.strftime('%Y-%m-%d'),
        'delivery_type': delivery_type,
        'delivery_address': customer['address'] if delivery_type == 'home' else '',
        'status': status,
        'tracking_status': tracking_status,
        'order_type': random.choice(['product', 'service']),
        'notes': f'ملاحظات عن الطلب {i}'
    }
    
    # Generar entre 1 y 5 elementos para cada pedido
    num_items = random.randint(1, 5)
    for j in range(num_items):
        product = random.choice(products)
        quantity = random.randint(1, 10)
        unit_price = product['price']
        item_total = quantity * unit_price
        total_amount += item_total
        
        order_item = {
            'order_number': order['order_number'],
            'product_code': product['code'],
            'product_name': product['name'],
            'quantity': quantity,
            'unit_price': unit_price,
            'item_type': random.choice(['fabric', 'accessory']),
            'processing_status': random.choice(['pending', 'processing', 'ready', 'delivered']),
            'notes': f'ملاحظات عن العنصر {j+1} في الطلب {i}'
        }
        order_items.append(order_item)
    
    # Actualizar el total del pedido
    order['total_amount'] = total_amount
    
    # Generar pagos aleatorios
    if random.random() > 0.3:  # 70% de probabilidad de tener algún pago
        payment_percentage = random.choice([0.25, 0.5, 0.75, 1.0])
        paid_amount = total_amount * payment_percentage
    
    order['paid_amount'] = paid_amount
    order['remaining_amount'] = total_amount - paid_amount
    
    orders.append(order)

df_orders = pd.DataFrame(orders)
df_orders.to_excel(writer, sheet_name='Orders', index=False)

df_order_items = pd.DataFrame(order_items)
df_order_items.to_excel(writer, sheet_name='OrderItems', index=False)

# 7. Datos de muestra para Pagos
payments = []
for order in orders:
    if order['paid_amount'] > 0:
        payment_date = datetime.strptime(order['order_date'], '%Y-%m-%d') + timedelta(days=random.randint(0, 5))
        payment = {
            'order_number': order['order_number'],
            'amount': order['paid_amount'],
            'payment_method': random.choice(['cash', 'bank_transfer', 'check']),
            'payment_date': payment_date.strftime('%Y-%m-%d'),
            'reference_number': f'REF{random.randint(10000, 99999)}',
            'notes': f'دفعة للطلب {order["order_number"]}'
        }
        payments.append(payment)

df_payments = pd.DataFrame(payments)
df_payments.to_excel(writer, sheet_name='Payments', index=False)

# Guardar el archivo Excel
writer.close()

print(f"Archivo de datos de muestra creado en: {excel_file}")
print("Este archivo contiene las siguientes hojas:")
print("1. Categories - فئات المنتجات")
print("2. Products - المنتجات")
print("3. Suppliers - الموردين")
print("4. CustomerCategories - فئات العملاء")
print("5. Customers - العملاء")
print("6. Orders - الطلبات")
print("7. OrderItems - عناصر الطلبات")
print("8. Payments - المدفوعات")
print("\nيمكنك استخدام هذا الملف لاستيراد البيانات إلى النظام من خلال صفحة استيراد البيانات.")
