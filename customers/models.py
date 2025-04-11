from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User

class Customer(models.Model):
    """
    Model for storing customer information
    """
    name = models.CharField(_('اسم العميل'), max_length=200)
    phone = models.CharField(_('رقم الهاتف'), max_length=20)
    address = models.TextField(_('العنوان'))
    email = models.EmailField(_('البريد الإلكتروني'), blank=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='customers_created',
        verbose_name=_('تم الإنشاء بواسطة')
    )
    notes = models.TextField(_('ملاحظات'), blank=True)
    
    class Meta:
        verbose_name = _('عميل')
        verbose_name_plural = _('العملاء')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

class Order(models.Model):
    """
    Model for customer orders
    """
    STATUS_CHOICES = [
        ('pending', _('قيد الانتظار')),
        ('processing', _('قيد التنفيذ')),
        ('completed', _('مكتمل')),
        ('cancelled', _('ملغي')),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('unpaid', _('غير مدفوع')),
        ('partial', _('مدفوع جزئياً')),
        ('paid', _('مدفوع بالكامل')),
    ]
    
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name=_('العميل')
    )
    order_number = models.CharField(_('رقم الطلب'), max_length=50, unique=True)
    order_date = models.DateTimeField(_('تاريخ الطلب'), auto_now_add=True)
    status = models.CharField(
        _('حالة الطلب'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    payment_status = models.CharField(
        _('حالة الدفع'),
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='unpaid'
    )
    total_amount = models.DecimalField(
        _('المبلغ الإجمالي'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    paid_amount = models.DecimalField(
        _('المبلغ المدفوع'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    delivery_date = models.DateField(_('تاريخ التسليم'), null=True, blank=True)
    notes = models.TextField(_('ملاحظات'), blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders_created',
        verbose_name=_('تم الإنشاء بواسطة')
    )
    
    class Meta:
        verbose_name = _('طلب')
        verbose_name_plural = _('الطلبات')
        ordering = ['-order_date']
    
    def __str__(self):
        return f"{self.order_number} - {self.customer.name}"
    
    @property
    def remaining_amount(self):
        """Calculate remaining amount to be paid"""
        return self.total_amount - self.paid_amount

class Payment(models.Model):
    """
    Model for tracking payments
    """
    PAYMENT_METHOD_CHOICES = [
        ('cash', _('نقداً')),
        ('bank_transfer', _('تحويل بنكي')),
        ('check', _('شيك')),
    ]
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('الطلب')
    )
    amount = models.DecimalField(_('المبلغ'), max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(_('تاريخ الدفع'), auto_now_add=True)
    payment_method = models.CharField(
        _('طريقة الدفع'),
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='cash'
    )
    reference_number = models.CharField(
        _('رقم المرجع'),
        max_length=50,
        blank=True,
        help_text=_('رقم الشيك أو التحويل البنكي')
    )
    notes = models.TextField(_('ملاحظات'), blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='payments_created',
        verbose_name=_('تم الإنشاء بواسطة')
    )
    
    class Meta:
        verbose_name = _('دفعة')
        verbose_name_plural = _('الدفعات')
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"{self.order.order_number} - {self.amount}"

    def save(self, *args, **kwargs):
        """Update order paid amount when payment is saved"""
        super().save(*args, **kwargs)
        # Update order paid amount
        order = self.order
        total_paid = sum(payment.amount for payment in order.payments.all())
        order.paid_amount = total_paid
        if total_paid >= order.total_amount:
            order.payment_status = 'paid'
        elif total_paid > 0:
            order.payment_status = 'partial'
        else:
            order.payment_status = 'unpaid'
        order.save()
