from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Department(models.Model):
    """
    Model for system departments
    """
    name = models.CharField(_('اسم القسم'), max_length=100)
    code = models.CharField(_('كود القسم'), max_length=20, unique=True)
    description = models.TextField(_('الوصف'), blank=True)
    icon = models.CharField(_('أيقونة'), max_length=50, default='fas fa-building')
    url_name = models.CharField(_('اسم URL'), max_length=100, help_text=_('اسم URL للقسم في نظام التوجيه'))
    is_active = models.BooleanField(_('نشط'), default=True)
    order = models.PositiveIntegerField(_('الترتيب'), default=0)
    
    class Meta:
        verbose_name = _('قسم')
        verbose_name_plural = _('الأقسام')
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name

class Branch(models.Model):
    code = models.CharField(_('كود الفرع'), max_length=3, unique=True)
    name = models.CharField(_('اسم الفرع'), max_length=100)
    address = models.TextField(_('العنوان'))
    phone = models.CharField(_('رقم الهاتف'), max_length=20)
    email = models.EmailField(_('البريد الإلكتروني'), blank=True)
    is_active = models.BooleanField(_('نشط'), default=True)
    is_main_branch = models.BooleanField(_('فرع رئيسي'), default=False)
    
    class Meta:
        verbose_name = _('فرع')
        verbose_name_plural = _('الفروع')
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"

    def save(self, *args, **kwargs):
        # Ensure branch code is in format '001', '002', etc.
        if self.code:
            self.code = self.code.zfill(3)
        super().save(*args, **kwargs)

class User(AbstractUser):
    branch = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT,
        related_name='users',
        verbose_name=_('الفرع'),
        null=True
    )
    
    phone = models.CharField(_('رقم الهاتف'), max_length=20, blank=True)
    departments = models.ManyToManyField(
        Department,
        verbose_name=_('الأقسام'),
        blank=True,
        related_name='users',
        help_text=_('الأقسام التي يمكن للمستخدم الوصول إليها')
    )
    
    class Meta:
        verbose_name = _('مستخدم')
        verbose_name_plural = _('المستخدمين')
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.branch})"
    
    def has_department_access(self, department_code):
        """Check if user has access to a specific department"""
        if self.is_superuser:
            return True
        return self.departments.filter(code=department_code, is_active=True).exists()

class Notification(models.Model):
    """
    Model for system notifications
    """
    PRIORITY_CHOICES = [
        ('low', _('منخفضة')),
        ('medium', _('متوسطة')),
        ('high', _('عالية')),
        ('urgent', _('عاجلة')),
    ]
    
    title = models.CharField(_('العنوان'), max_length=255)
    message = models.TextField(_('الرسالة'))
    priority = models.CharField(_('الأولوية'), max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Sender information
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
        verbose_name=_('المرسل')
    )
    sender_department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
        verbose_name=_('قسم المرسل')
    )
    
    # Target information
    target_department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='received_notifications',
        verbose_name=_('القسم المستهدف')
    )
    target_branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name='received_notifications',
        verbose_name=_('الفرع المستهدف'),
        null=True,
        blank=True
    )
    
    # Related object (generic foreign key)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')
    
    # Timestamps
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    # Status
    is_read = models.BooleanField(_('مقروءة'), default=False)
    read_at = models.DateTimeField(_('تاريخ القراءة'), null=True, blank=True)
    read_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='read_notifications',
        verbose_name=_('قرأت بواسطة'),
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = _('إشعار')
        verbose_name_plural = _('الإشعارات')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def mark_as_read(self, user):
        """Mark notification as read by user"""
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.read_by = user
        self.save()

class CompanyInfo(models.Model):
    """
    Model for company information
    """
    name = models.CharField(_('اسم الشركة'), max_length=255)
    logo = models.ImageField(_('شعار الشركة'), upload_to='company/', null=True, blank=True)
    description = models.TextField(_('وصف الشركة'), blank=True, default="نظام متكامل لإدارة العملاء والمبيعات والإنتاج والمخزون")
    address = models.TextField(_('العنوان'))
    phone = models.CharField(_('رقم الهاتف'), max_length=20)
    email = models.EmailField(_('البريد الإلكتروني'))
    website = models.URLField(_('الموقع الإلكتروني'), blank=True)
    tax_number = models.CharField(_('الرقم الضريبي'), max_length=50, blank=True)
    commercial_register = models.CharField(_('السجل التجاري'), max_length=50, blank=True)
    
    # Social media
    facebook = models.URLField(_('فيسبوك'), blank=True)
    twitter = models.URLField(_('تويتر'), blank=True)
    instagram = models.URLField(_('انستغرام'), blank=True)
    linkedin = models.URLField(_('لينكد إن'), blank=True)
    
    # Additional information
    about = models.TextField(_('نبذة عن الشركة'), blank=True)
    vision = models.TextField(_('رؤية الشركة'), blank=True)
    mission = models.TextField(_('رسالة الشركة'), blank=True)
    
    # System settings
    primary_color = models.CharField(_('اللون الرئيسي'), max_length=7, default='#007bff')
    secondary_color = models.CharField(_('اللون الثانوي'), max_length=7, default='#6c757d')
    accent_color = models.CharField(_('لون التمييز'), max_length=7, default='#28a745')
    
    class Meta:
        verbose_name = _('معلومات الشركة')
        verbose_name_plural = _('معلومات الشركة')
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and CompanyInfo.objects.exists():
            # Update existing instance
            existing = CompanyInfo.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)

class FormField(models.Model):
    """
    Model for customizable form fields
    """
    FORM_CHOICES = [
        ('order', _('نموذج الطلب')),
        ('customer', _('نموذج العميل')),
        ('production', _('نموذج الإنتاج')),
        ('inspection', _('نموذج المعاينة')),
        ('installation', _('نموذج التركيب')),
    ]
    
    FIELD_TYPE_CHOICES = [
        ('text', _('نص')),
        ('number', _('رقم')),
        ('date', _('تاريخ')),
        ('datetime', _('تاريخ ووقت')),
        ('select', _('قائمة اختيار')),
        ('checkbox', _('مربع اختيار')),
        ('radio', _('زر راديو')),
        ('textarea', _('منطقة نص')),
        ('file', _('ملف')),
        ('image', _('صورة')),
    ]
    
    form_type = models.CharField(_('نوع النموذج'), max_length=20, choices=FORM_CHOICES)
    field_name = models.CharField(_('اسم الحقل'), max_length=100)
    field_label = models.CharField(_('عنوان الحقل'), max_length=255)
    field_type = models.CharField(_('نوع الحقل'), max_length=20, choices=FIELD_TYPE_CHOICES)
    required = models.BooleanField(_('مطلوب'), default=False)
    enabled = models.BooleanField(_('مفعل'), default=True)
    order = models.PositiveIntegerField(_('الترتيب'), default=0)
    
    # For select, radio, and checkbox fields
    choices = models.TextField(_('الخيارات'), blank=True, help_text=_('أدخل الخيارات مفصولة بفاصلة'))
    
    # Validation
    min_length = models.PositiveIntegerField(_('الحد الأدنى للطول'), null=True, blank=True)
    max_length = models.PositiveIntegerField(_('الحد الأقصى للطول'), null=True, blank=True)
    min_value = models.FloatField(_('الحد الأدنى للقيمة'), null=True, blank=True)
    max_value = models.FloatField(_('الحد الأقصى للقيمة'), null=True, blank=True)
    
    # Help text
    help_text = models.CharField(_('نص المساعدة'), max_length=255, blank=True)
    
    # Default value
    default_value = models.CharField(_('القيمة الافتراضية'), max_length=255, blank=True)
    
    class Meta:
        verbose_name = _('حقل نموذج')
        verbose_name_plural = _('حقول النماذج')
        ordering = ['form_type', 'order']
        unique_together = ['form_type', 'field_name']
    
    def __str__(self):
        return f"{self.get_form_type_display()} - {self.field_label}"
    
    def get_choices_list(self):
        """Return choices as a list"""
        if not self.choices:
            return []
        return [choice.strip() for choice in self.choices.split(',')]
