from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    Custom user model to extend Django's built-in User model
    """
    image = models.ImageField(_('صورة المستخدم'), upload_to='users/', null=True, blank=True)
    phone = models.CharField(_('رقم الهاتف'), max_length=20, blank=True)
    address = models.TextField(_('العنوان'), blank=True)
    role = models.CharField(
        _('الدور'),
        max_length=20,
        choices=[
            ('admin', _('مدير')),
            ('manager', _('مشرف')),
            ('employee', _('موظف')),
            ('factory_worker', _('عامل مصنع')),
        ],
        default='employee'
    )
    
    class Meta:
        verbose_name = _('مستخدم')
        verbose_name_plural = _('المستخدمين')
        
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

class CompanyInfo(models.Model):
    """
    Model to store company information
    """
    name = models.CharField(_('اسم الشركة'), max_length=100)
    logo = models.ImageField(_('شعار الشركة'), upload_to='company/')
    address = models.TextField(_('عنوان الشركة'))
    phone = models.CharField(_('رقم الهاتف'), max_length=20)
    email = models.EmailField(_('البريد الإلكتروني'))
    tax_number = models.CharField(_('الرقم الضريبي'), max_length=50, blank=True)
    commercial_record = models.CharField(_('السجل التجاري'), max_length=50, blank=True)
    
    class Meta:
        verbose_name = _('معلومات الشركة')
        verbose_name_plural = _('معلومات الشركة')
        
    def __str__(self):
        return self.name

class Notification(models.Model):
    """
    Model for system notifications
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(_('العنوان'), max_length=200)
    message = models.TextField(_('الرسالة'))
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    read = models.BooleanField(_('مقروءة'), default=False)
    
    class Meta:
        verbose_name = _('إشعار')
        verbose_name_plural = _('الإشعارات')
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title
