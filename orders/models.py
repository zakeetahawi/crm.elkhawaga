from django.db import models
from django.conf import settings
from customers.models import Customer
from inventory.models import Product

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('processing', 'قيد التنفيذ'),
        ('completed', 'مكتمل'),
        ('cancelled', 'ملغي'),
    ]
    
    ORDER_TYPE_CHOICES = [
        ('goods', 'سلع'),
        ('services', 'خدمات'),
    ]
    
    GOODS_TYPE_CHOICES = [
        ('accessories', 'اكسسوار'),
        ('fabric', 'قماش'),
    ]
    
    SERVICE_TYPE_CHOICES = [
        ('inspection', 'معاينة'),
        ('tailoring', 'تفصيل'),
        ('installation', 'تركيب'),
        ('transport', 'نقل'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='customer_orders', verbose_name='العميل')
    order_number = models.CharField(max_length=50, unique=True, verbose_name='رقم الطلب')
    order_date = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الطلب')
    delivery_date = models.DateField(null=True, blank=True, verbose_name='تاريخ التسليم')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='حالة الطلب')
    
    # New fields for order types
    order_type = models.CharField(max_length=10, choices=ORDER_TYPE_CHOICES, verbose_name='نوع الطلب')
    goods_type = models.CharField(max_length=15, choices=GOODS_TYPE_CHOICES, null=True, blank=True, verbose_name='نوع السلعة')
    service_type = models.CharField(max_length=15, choices=SERVICE_TYPE_CHOICES, null=True, blank=True, verbose_name='نوع الخدمة')
    invoice_number = models.CharField(max_length=50, null=True, blank=True, verbose_name='رقم الفاتورة')
    contract_number = models.CharField(max_length=50, null=True, blank=True, verbose_name='رقم العقد')
    payment_verified = models.BooleanField(default=False, verbose_name='تم التحقق من السداد')
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='المبلغ الإجمالي')
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='المبلغ المدفوع')
    notes = models.TextField(blank=True, verbose_name='ملاحظات')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='تم الإنشاء بواسطة')
    branch = models.ForeignKey('accounts.Branch', on_delete=models.CASCADE, related_name='branch_orders', verbose_name='الفرع', null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')

    class Meta:
        verbose_name = 'طلب'
        verbose_name_plural = 'الطلبات'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.order_number} - {self.customer.name}'

    @property
    def remaining_amount(self):
        """Calculate remaining amount to be paid"""
        return self.total_amount - self.paid_amount

    @property
    def is_fully_paid(self):
        """Check if order is fully paid"""
        return self.paid_amount >= self.total_amount

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='الطلب')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items', verbose_name='المنتج')
    quantity = models.PositiveIntegerField(verbose_name='الكمية')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='سعر الوحدة')
    notes = models.TextField(blank=True, verbose_name='ملاحظات')

    class Meta:
        verbose_name = 'عنصر الطلب'
        verbose_name_plural = 'عناصر الطلب'

    def __str__(self):
        return f'{self.product.name} ({self.quantity})'

    @property
    def total_price(self):
        """Calculate total price for this item"""
        return self.quantity * self.unit_price

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'نقداً'),
        ('bank_transfer', 'تحويل بنكي'),
        ('check', 'شيك'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments', verbose_name='الطلب')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='المبلغ')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash', verbose_name='طريقة الدفع')
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الدفع')
    reference_number = models.CharField(max_length=100, blank=True, verbose_name='رقم المرجع')
    notes = models.TextField(blank=True, verbose_name='ملاحظات')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='تم الإنشاء بواسطة')

    class Meta:
        verbose_name = 'دفعة'
        verbose_name_plural = 'الدفعات'
        ordering = ['-payment_date']

    def __str__(self):
        return f'{self.order.order_number} - {self.amount} ({self.get_payment_method_display()})'

    def save(self, *args, **kwargs):
        """Update order's paid amount when payment is saved"""
        super().save(*args, **kwargs)
        # Update order's paid amount
        total_payments = Payment.objects.filter(order=self.order).aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        self.order.paid_amount = total_payments
        self.order.save()
