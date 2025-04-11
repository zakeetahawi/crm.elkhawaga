from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from customers.models import Order

class ProductionLine(models.Model):
    """
    Model for different production lines in the factory
    """
    name = models.CharField(_('اسم خط الإنتاج'), max_length=100)
    description = models.TextField(_('الوصف'), blank=True)
    is_active = models.BooleanField(_('نشط'), default=True)
    
    class Meta:
        verbose_name = _('خط إنتاج')
        verbose_name_plural = _('خطوط الإنتاج')
    
    def __str__(self):
        return self.name

class ProductionOrder(models.Model):
    """
    Model for production orders in the factory
    """
    STATUS_CHOICES = [
        ('pending', _('قيد الانتظار')),
        ('in_progress', _('جاري التصنيع')),
        ('quality_check', _('فحص الجودة')),
        ('completed', _('مكتمل')),
        ('cancelled', _('ملغي')),
    ]
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='production_orders',
        verbose_name=_('الطلب')
    )
    production_line = models.ForeignKey(
        ProductionLine,
        on_delete=models.SET_NULL,
        null=True,
        related_name='production_orders',
        verbose_name=_('خط الإنتاج')
    )
    status = models.CharField(
        _('الحالة'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    start_date = models.DateTimeField(_('تاريخ البدء'), null=True, blank=True)
    end_date = models.DateTimeField(_('تاريخ الانتهاء'), null=True, blank=True)
    estimated_completion = models.DateTimeField(_('التاريخ المتوقع للانتهاء'), null=True)
    notes = models.TextField(_('ملاحظات'), blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='production_orders_created',
        verbose_name=_('تم الإنشاء بواسطة')
    )
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('أمر إنتاج')
        verbose_name_plural = _('أوامر الإنتاج')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"أمر إنتاج - {self.order.order_number}"

class ProductionStage(models.Model):
    """
    Model for tracking different stages of production
    """
    production_order = models.ForeignKey(
        ProductionOrder,
        on_delete=models.CASCADE,
        related_name='stages',
        verbose_name=_('أمر الإنتاج')
    )
    name = models.CharField(_('اسم المرحلة'), max_length=100)
    description = models.TextField(_('الوصف'), blank=True)
    start_date = models.DateTimeField(_('تاريخ البدء'), null=True, blank=True)
    end_date = models.DateTimeField(_('تاريخ الانتهاء'), null=True, blank=True)
    completed = models.BooleanField(_('مكتملة'), default=False)
    notes = models.TextField(_('ملاحظات'), blank=True)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_stages',
        verbose_name=_('تم التعيين إلى')
    )
    
    class Meta:
        verbose_name = _('مرحلة إنتاج')
        verbose_name_plural = _('مراحل الإنتاج')
        ordering = ['start_date']
    
    def __str__(self):
        return f"{self.name} - {self.production_order}"

class QualityCheck(models.Model):
    """
    Model for quality control checks
    """
    RESULT_CHOICES = [
        ('passed', _('ناجح')),
        ('failed', _('راسب')),
        ('needs_rework', _('يحتاج إعادة تصنيع')),
    ]
    
    production_order = models.ForeignKey(
        ProductionOrder,
        on_delete=models.CASCADE,
        related_name='quality_checks',
        verbose_name=_('أمر الإنتاج')
    )
    checked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='quality_checks_performed',
        verbose_name=_('تم الفحص بواسطة')
    )
    check_date = models.DateTimeField(_('تاريخ الفحص'), auto_now_add=True)
    result = models.CharField(
        _('النتيجة'),
        max_length=20,
        choices=RESULT_CHOICES
    )
    notes = models.TextField(_('ملاحظات'), blank=True)
    
    class Meta:
        verbose_name = _('فحص جودة')
        verbose_name_plural = _('فحوصات الجودة')
        ordering = ['-check_date']
    
    def __str__(self):
        return f"فحص جودة - {self.production_order} - {self.get_result_display()}"
