from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Order, OrderItem, Payment
# These models are already defined in models.py
from .models import Order, OrderItem, Payment

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer', 'order_number', 'delivery_date', 'status', 'notes']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'order_number': forms.TextInput(attrs={'class': 'form-control'}),
            'delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'unit_price', 'notes']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'reference_number', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

# Formset for managing multiple order items
OrderItemFormSet = forms.inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    extra=1,
    can_delete=True,
)

# ExtendedOrderForm is merged into the main OrderForm since the fields are now in Order model
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'customer', 'order_number', 'delivery_date', 'status',
            'order_type', 'goods_type', 'service_type', 'invoice_number',
            'contract_number', 'payment_verified', 'branch', 'notes'
        ]
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'order_number': forms.TextInput(attrs={'class': 'form-control'}),
            'delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'order_type': forms.Select(attrs={'class': 'form-select'}),
            'goods_type': forms.Select(attrs={'class': 'form-select'}),
            'service_type': forms.Select(attrs={'class': 'form-select'}),
            'invoice_number': forms.TextInput(attrs={'class': 'form-control'}),
            'contract_number': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_verified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['goods_type'].required = False
        self.fields['service_type'].required = False
        self.fields['invoice_number'].required = False
        self.fields['contract_number'].required = False
