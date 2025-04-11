# نظام الخواجه لإدارة العملاء (CRM)

## نظرة عامة
نظام إدارة العملاء الشامل "الخواجه" مصمم لدعم الشركات في إدارة عملائها، والمبيعات، والإنتاج، والمخزون بكفاءة عالية.

## المميزات الرئيسية
- إدارة العملاء
- تتبع الطلبات والمبيعات
- إدارة المخزون
- نظام إنتاج متكامل
- تقارير وإحصائيات متقدمة

## المتطلبات التقنية
- Python 3.13+
- Django 5.2
- PostgreSQL
- Redis

## إعداد المشروع

### 1. استنساخ المستودع
```bash
git clone https://github.com/yourusername/elkhawaga-crm.git
cd elkhawaga-crm
```

### 2. إنشاء بيئة افتراضية
```bash
python -m venv venv
source venv/bin/activate  # على Linux/macOS
venv\Scripts\activate  # على Windows
```

### 3. تثبيت التبعيات
```bash
pip install -r requirements.txt
```

### 4. إعداد قاعدة البيانات
```bash
# إنشاء قاعدة بيانات PostgreSQL
createdb elkhawaga_db

# تطبيق الهجرات
python manage.py makemigrations
python manage.py migrate
```

### 5. إنشاء مستخدم مسؤول
```bash
python manage.py createsuperuser
```

### 6. تشغيل الخادم
```bash
python manage.py runserver
```

## التكوين
- قم بتعديل `crm/settings.py` لتكوين إعدادات المشروع
- تأكد من تكوين متغيرات البيئة للإعدادات الحساسة

## المساهمة
1. قم بعمل fork للمشروع
2. أنشئ branch جديد (`git checkout -b feature/AmazingFeature`)
3. التزم بتغييراتك (`git commit -m 'Add some AmazingFeature'`)
4. ادفع إلى البرانش (`git push origin feature/AmazingFeature`)
5. افتح طلب سحب

## الترخيص
موزع تحت رخصة MIT. راجع `LICENSE` للمزيد من المعلومات.

## جهات الاتصال
- المطور: [اسمك]
- البريد الإلكتروني: [بريدك الإلكتروني]
- رابط المشروع: [رابط المشروع]
# crm.elkhawaga
