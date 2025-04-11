from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from accounts.models import User

class Category(models.Model):
    """
    Model for product categories
    """
    name = models.CharField(_('اسم الفئة'), max_length=100)
    description = models.TextField(_('الوصف'), blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('الفئة الأب')
    )
    
    class Meta:
        verbose_name = _('فئة')
        verbose_name_plural = _('الفئات')
        ordering = ['name']
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} - {self.name}"
        return self.name

class Product(models.Model):
    """
    Model for products
    """
    UNIT_CHOICES = [
        ('piece', _('قطعة')),
        ('meter', _('متر')),
        ('sqm', _('متر مربع')),
        ('kg', _('كيلوجرام')),
    ]
    
    name = models.CharField(_('اسم المنتج'), max_length=200)
    code = models.CharField(_('كود المنتج'), max_length=50, unique=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products',
        verbose_name=_('الفئة')
    )
    description = models.TextField(_('الوصف'), blank=True)
    unit = models.CharField(
        _('وحدة القياس'),
        max_length=10,
        choices=UNIT_CHOICES,
        default='piece'
    )
    price = models.DecimalField(
        _('السعر'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    minimum_stock = models.PositiveIntegerField(
        _('الحد الأدنى للمخزون'),
        default=0
    )
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    class Meta:
        verbose_name = _('منتج')
        verbose_name_plural = _('المنتجات')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    @property
    def current_stock(self):
        """Get current stock level"""
        stock_ins = sum(transaction.quantity for transaction in 
                       self.stock_transactions.filter(transaction_type='in'))
        stock_outs = sum(transaction.quantity for transaction in 
                        self.stock_transactions.filter(transaction_type='out'))
        return stock_ins - stock_outs
    
    @property
    def needs_restock(self):
        """Check if product needs restocking"""
        return self.current_stock <= self.minimum_stock

class StockTransaction(models.Model):
    """
    Model for tracking stock movements
    """
    TRANSACTION_TYPES = [
        ('in', _('وارد')),
        ('out', _('صادر')),
    ]
    
    TRANSACTION_REASONS = [
        ('purchase', _('شراء')),
        ('sale', _('بيع')),
        ('return', _('مرتجع')),
        ('damage', _('تالف')),
        ('adjustment', _('تسوية')),
    ]
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stock_transactions',
        verbose_name=_('المنتج')
    )
    transaction_type = models.CharField(
        _('نوع الحركة'),
        max_length=3,
        choices=TRANSACTION_TYPES
    )
    reason = models.CharField(
        _('السبب'),
        max_length=20,
        choices=TRANSACTION_REASONS
    )
    quantity = models.PositiveIntegerField(_('الكمية'))
    date = models.DateTimeField(_('التاريخ'), auto_now_add=True)
    reference = models.CharField(_('المرجع'), max_length=100, blank=True)
    notes = models.TextField(_('ملاحظات'), blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='stock_transactions',
        verbose_name=_('تم الإنشاء بواسطة')
    )
    
    class Meta:
        verbose_name = _('حركة مخزون')
        verbose_name_plural = _('حركات المخزون')
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.product.name} - {self.quantity}"
    
    def clean(self):
        """Validate stock transaction"""
        if self.transaction_type == 'out' and self.quantity > self.product.current_stock:
            raise ValidationError(_('الكمية المطلوبة غير متوفرة في المخزون'))

class Supplier(models.Model):
    """
    Model for suppliers
    """
    name = models.CharField(_('اسم المورد'), max_length=200)
    contact_person = models.CharField(_('الشخص المسؤول'), max_length=100)
    phone = models.CharField(_('رقم الهاتف'), max_length=20)
    email = models.EmailField(_('البريد الإلكتروني'), blank=True)
    address = models.TextField(_('العنوان'))
    tax_number = models.CharField(_('الرقم الضريبي'), max_length=50, blank=True)
    notes = models.TextField(_('ملاحظات'), blank=True)
    
    class Meta:
        verbose_name = _('مورد')
        verbose_name_plural = _('الموردين')
        ordering = ['name']
    
    def __str__(self):
        return self.name

class PurchaseOrder(models.Model):
    """
    Model for purchase orders
    """
    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('ordered', _('تم الطلب')),
        ('received', _('تم الاستلام')),
        ('cancelled', _('ملغي')),
    ]
    
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='purchase_orders',
        verbose_name=_('المورد')
    )
    order_number = models.CharField(_('رقم الطلب'), max_length=50, unique=True)
    order_date = models.DateTimeField(_('تاريخ الطلب'), auto_now_add=True)
    expected_date = models.DateField(_('تاريخ التوريد المتوقع'), null=True, blank=True)
    status = models.CharField(
        _('الحالة'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    total_amount = models.DecimalField(
        _('المبلغ الإجمالي'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    notes = models.TextField(_('ملاحظات'), blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='purchase_orders_created',
        verbose_name=_('تم الإنشاء بواسطة')
    )
    
    class Meta:
        verbose_name = _('طلب شراء')
        verbose_name_plural = _('طلبات الشراء')
        ordering = ['-order_date']
    
    def __str__(self):
        return f"{self.order_number} - {self.supplier.name}"
