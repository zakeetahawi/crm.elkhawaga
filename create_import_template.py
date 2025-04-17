import os
import sys
import django

# إعداد بيئة Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from data_import_export.utils import generate_multi_sheet_template

def create_template():
    """
    إنشاء ملف Excel نموذجي متعدد الصفحات للاستيراد
    """
    # قائمة النماذج التي سيتم تضمينها في القالب
    model_names = [
        'inventory.product',
        'inventory.supplier',
        'customers.customer',
        'orders.order',
        'inventory.category',
        'customers.customercategory',
        'orders.orderitem',
        'orders.payment',
    ]
    
    # إنشاء القالب
    output = generate_multi_sheet_template(model_names)
    
    # التأكد من وجود مجلد data_files
    if not os.path.exists('data_files'):
        os.makedirs('data_files')
    
    # حفظ القالب
    with open('data_files/import_template.xlsx', 'wb') as f:
        f.write(output.getvalue())
    
    print("تم إنشاء ملف القالب بنجاح في: data_files/import_template.xlsx")

if __name__ == '__main__':
    create_template()
