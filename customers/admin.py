from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Customer, Order, Payment

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'phone', 'email', 'address')
    readonly_fields = ('created_at', 'created_by')
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'status', 'payment_status', 'total_amount', 'order_date')
    list_filter = ('status', 'payment_status', 'order_date')
    search_fields = ('order_number', 'customer__name', 'notes')
    readonly_fields = ('order_date', 'created_by')
    
    fieldsets = (
        (_('معلومات الطلب'), {
            'fields': ('order_number', 'customer', 'status', 'delivery_date')
        }),
        (_('المعلومات المالية'), {
            'fields': ('total_amount', 'paid_amount', 'payment_status')
        }),
        (_('ملاحظات إضافية'), {
            'fields': ('notes',)
        }),
        (_('معلومات النظام'), {
            'fields': ('created_by', 'order_date'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount', 'payment_method', 'payment_date')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('order__order_number', 'reference_number', 'notes')
    readonly_fields = ('payment_date', 'created_by')
    
    fieldsets = (
        (_('معلومات الدفع'), {
            'fields': ('order', 'amount', 'payment_method', 'reference_number')
        }),
        (_('ملاحظات إضافية'), {
            'fields': ('notes',)
        }),
        (_('معلومات النظام'), {
            'fields': ('created_by', 'payment_date'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
