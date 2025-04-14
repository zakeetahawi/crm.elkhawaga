from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Order, OrderItem, Payment
from .forms import OrderForm, OrderItemFormSet, PaymentForm
from accounts.models import Branch

@login_required
def order_list(request):
    """
    View for displaying the list of orders with search and filtering
    """
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    # Filter orders based on search query and status
    orders = Order.objects.all()
    
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(customer__name__icontains=search_query)
        )
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Order by created_at
    orders = orders.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(orders, 10)  # Show 10 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'total_orders': orders.count(),
    }
    
    return render(request, 'orders/order_list.html', context)

@login_required
def order_detail(request, pk):
    """
    View for displaying order details
    """
    order = get_object_or_404(Order, pk=pk)
    payments = order.payments.all().order_by('-payment_date')
    
    # Now all information is in the Order model
    order_items = order.items.all()
    
    context = {
        'order': order,
        'payments': payments,
        'order_items': order_items,
    }
    
    return render(request, 'orders/order_detail.html', context)

@login_required
def order_create(request):
    """
    View for creating a new order
    """
    if request.method == 'POST':
        form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            try:
                # Save order
                order = form.save(commit=False)
                order.created_by = request.user
                # Set branch to user's branch if not provided
                if not order.branch:
                    order.branch = request.user.branch
                order.save()
                
                # Save order items
                formset.instance = order
                formset.save()
                
                # Calculate total amount
                total_amount = sum(item.quantity * item.unit_price for item in order.items.all())
                order.total_amount = total_amount
                order.save()
                
                # Create notification for inventory department
                from accounts.models import Notification, Department
                inventory_dept = Department.objects.filter(code='inventory').first()
                if inventory_dept:
                    try:
                        # Create notification data
                        notification_data = {
                            'title': 'طلب جديد يحتاج للتحقق من المخزون',
                            'message': f'تم إنشاء طلب جديد رقم {order.order_number} ويحتاج للتحقق من توفر المنتجات في المخزون',
                            'priority': 'medium',
                            'sender': request.user,
                            'target_department': inventory_dept,
                            'target_branch': order.branch,
                        }
                        
                        # Add sender department if exists
                        if hasattr(request.user, 'departments') and request.user.departments.exists():
                            notification_data['sender_department'] = request.user.departments.first()
                        
                        # Create notification
                        Notification.objects.create(**notification_data)
                        print("Notification created successfully")
                    except Exception as notification_error:
                        # Log the error but don't prevent order creation
                        print(f"Error creating notification: {notification_error}")
                
                messages.success(request, 'تم إنشاء الطلب بنجاح.')
                print("Redirecting to order detail page:", order.pk)
                return redirect('orders:order_detail', pk=order.pk)
            except Exception as e:
                print("Error saving order:", str(e))
                messages.error(request, f'حدث خطأ أثناء حفظ الطلب: {str(e)}')
    else:
        form = OrderForm()
        formset = OrderItemFormSet()
        
        # Set default branch to user's branch
        if not request.user.is_superuser:
            form.fields['branch'].initial = request.user.branch
            form.fields['branch'].queryset = Branch.objects.filter(id=request.user.branch.id)
    
    context = {
        'form': form,
        'formset': formset,
        'title': 'إنشاء طلب جديد',
    }
    
    return render(request, 'orders/order_form.html', context)

@login_required
def order_update(request, pk):
    """
    View for updating an existing order
    """
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        formset = OrderItemFormSet(request.POST, instance=order)
        
        if form.is_valid() and formset.is_valid():
            # Save order
            order = form.save()
            formset.save()
            
            # Recalculate total amount
            total_amount = sum(item.quantity * item.unit_price for item in order.items.all())
            order.total_amount = total_amount
            order.save()
            
            # Create notification for inventory department
            from accounts.models import Notification, Department
            inventory_dept = Department.objects.filter(code='inventory').first()
            if inventory_dept:
                try:
                    # Create notification data
                    notification_data = {
                        'title': 'طلب تم تحديثه يحتاج للتحقق من المخزون',
                        'message': f'تم تحديث الطلب رقم {order.order_number} ويحتاج للتحقق من توفر المنتجات في المخزون',
                        'priority': 'medium',
                        'sender': request.user,
                        'target_department': inventory_dept,
                        'target_branch': order.branch,
                    }
                    
                    # Add sender department if exists
                    if hasattr(request.user, 'departments') and request.user.departments.exists():
                        notification_data['sender_department'] = request.user.departments.first()
                    
                    # Create notification
                    Notification.objects.create(**notification_data)
                except Exception as notification_error:
                    # Log the error but don't prevent order update
                    print(f"Error creating notification: {notification_error}")
            
            messages.success(request, 'تم تحديث الطلب بنجاح.')
            return redirect('orders:order_detail', pk=order.pk)
    else:
        form = OrderForm(instance=order)
        formset = OrderItemFormSet(instance=order)
        
        # Set default branch to user's branch
        if not request.user.is_superuser:
            form.fields['branch'].initial = request.user.branch
            form.fields['branch'].queryset = Branch.objects.filter(id=request.user.branch.id)
    
    context = {
        'form': form,
        'formset': formset,
        'order': order,
        'title': 'تعديل الطلب',
    }
    
    return render(request, 'orders/order_form.html', context)

@login_required
def order_delete(request, pk):
    """
    View for deleting an order
    """
    order = get_object_or_404(Order, pk=pk)
    
    if request.method == 'POST':
        order.delete()
        messages.success(request, 'تم حذف الطلب بنجاح.')
        return redirect('orders:order_list')
    
    context = {
        'order': order,
    }
    
    return render(request, 'orders/order_confirm_delete.html', context)

@login_required
def payment_create(request, order_pk):
    """
    View for creating a new payment for an order
    """
    order = get_object_or_404(Order, pk=order_pk)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.order = order
            payment.created_by = request.user
            payment.save()
            
            messages.success(request, 'تم تسجيل الدفعة بنجاح.')
            return redirect('orders:order_detail', pk=order.pk)
    else:
        form = PaymentForm()
    
    context = {
        'form': form,
        'order': order,
        'title': 'تسجيل دفعة جديدة',
    }
    
    return render(request, 'orders/payment_form.html', context)

@login_required
def payment_delete(request, pk):
    """
    View for deleting a payment
    """
    payment = get_object_or_404(Payment, pk=pk)
    order = payment.order
    
    if request.method == 'POST':
        payment.delete()
        messages.success(request, 'تم حذف الدفعة بنجاح.')
        return redirect('orders:order_detail', pk=order.pk)
    
    context = {
        'payment': payment,
        'order': order,
    }
    
    return render(request, 'orders/payment_confirm_delete.html', context)

# Views for accessory items and fabric orders are now integrated into the main Order model
