from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import ProductionLine, ProductionOrder, ProductionStage, QualityCheck

@admin.register(ProductionLine)
class ProductionLineAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')

@admin.register(ProductionOrder)
class ProductionOrderAdmin(admin.ModelAdmin):
    list_display = ('order', 'production_line', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('order__order_number', 'notes')
    readonly_fields = ('created_at', 'created_by')
    
    fieldsets = (
        (_('معلومات أمر الإنتاج'), {
            'fields': ('order', 'production_line', 'status')
        }),
        (_('التواريخ'), {
            'fields': ('start_date', 'end_date', 'estimated_completion')
        }),
        (_('ملاحظات إضافية'), {
            'fields': ('notes',)
        }),
        (_('معلومات النظام'), {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(ProductionStage)
class ProductionStageAdmin(admin.ModelAdmin):
    list_display = ('name', 'production_order', 'start_date', 'end_date', 'completed')
    list_filter = ('completed', 'start_date', 'end_date')
    search_fields = ('name', 'description', 'production_order__order__order_number')
    
    fieldsets = (
        (_('معلومات مرحلة الإنتاج'), {
            'fields': ('production_order', 'name', 'description')
        }),
        (_('التواريخ'), {
            'fields': ('start_date', 'end_date', 'completed')
        }),
        (_('التعيين'), {
            'fields': ('assigned_to', 'notes')
        }),
    )

@admin.register(QualityCheck)
class QualityCheckAdmin(admin.ModelAdmin):
    list_display = ('production_order', 'check_date', 'result', 'checked_by')
    list_filter = ('result', 'check_date')
    search_fields = ('production_order__order__order_number', 'notes')
    readonly_fields = ('check_date',)
    
    fieldsets = (
        (_('معلومات فحص الجودة'), {
            'fields': ('production_order', 'result')
        }),
        (_('التفاصيل'), {
            'fields': ('checked_by', 'notes')
        }),
        (_('معلومات النظام'), {
            'fields': ('check_date',),
            'classes': ('collapse',)
        }),
    )
