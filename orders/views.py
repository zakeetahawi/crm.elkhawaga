from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Order, OrderItem, Payment
from .extended_models import ExtendedOrder, AccessoryItem, FabricOrder
from .forms import OrderForm, OrderItemFormSet, PaymentForm, ExtendedOrderForm, AccessoryItemFormSet, FabricOrderForm
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
    
    # Get extended order information if it exists
    try:
        extended_order = order.extended_info
        accessory_items = extended_order.accessory_items.all()
        
        # Get fabric order if it exists
        try:
            fabric_order = extended_order.fabric_order
        except:
            fabric_order = None
    except:
        extended_order = None
        accessory_items = None
        fabric_order = None
    
    context = {
        'order': order,
        'payments': payments,
        'extended_order': extended_order,
        'accessory_items': accessory_items,
        'fabric_order': fabric_order,
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
        extended_form = ExtendedOrderForm(request.POST)
        
        # Debug information
        print("Form is valid:", form.is_valid())
        if not form.is_valid():
            print("Form errors:", form.errors)
        
        print("Formset is valid:", formset.is_valid())
        if not formset.is_valid():
            print("Formset errors:", formset.errors)
            for i, form_errors in enumerate(formset.errors):
                if form_errors:
                    print(f"Form {i} errors:", form_errors)
        
        print("Extended form is valid:", extended_form.is_valid())
        if not extended_form.is_valid():
            print("Extended form errors:", extended_form.errors)
        
        if form.is_valid() and formset.is_valid() and extended_form.is_valid():
            try:
                # Save order
                order = form.save(commit=False)
                order.created_by = request.user
                order.save()
                print("Order saved successfully:", order.id)
                
                # Save order items
                formset.instance = order
                formset.save()
                print("Order items saved successfully")
                
                # Calculate total amount
                total_amount = sum(item.quantity * item.unit_price for item in order.items.all())
                order.total_amount = total_amount
                order.save()
                print("Total amount calculated and saved:", total_amount)
                
                # Save extended order information
                extended_order = extended_form.save(commit=False)
                extended_order.order = order
                
                # Set branch to user's branch if not provided
                if not extended_order.branch:
                    extended_order.branch = request.user.branch
                    
                extended_order.save()
                print("Extended order saved successfully")
                
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
                            'target_branch': extended_order.branch,
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
        extended_form = ExtendedOrderForm()
        
        # Set default branch to user's branch
        if not request.user.is_superuser:
            extended_form.fields['branch'].initial = request.user.branch
            extended_form.fields['branch'].queryset = Branch.objects.filter(id=request.user.branch.id)
    
    context = {
        'form': form,
        'formset': formset,
        'extended_form': extended_form,
        'title': 'إنشاء طلب جديد',
    }
    
    return render(request, 'orders/order_form.html', context)

@login_required
def order_update(request, pk):
    """
    View for updating an existing order
    """
    order = get_object_or_404(Order, pk=pk)
    
    # Get or create extended order
    try:
        extended_order = order.extended_info
    except ExtendedOrder.DoesNotExist:
        extended_order = None
    
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        formset = OrderItemFormSet(request.POST, instance=order)
        
        if extended_order:
            extended_form = ExtendedOrderForm(request.POST, instance=extended_order)
        else:
            extended_form = ExtendedOrderForm(request.POST)
        
        if form.is_valid() and formset.is_valid() and extended_form.is_valid():
            # Save order
            order = form.save()
            formset.save()
            
            # Recalculate total amount
            total_amount = sum(item.quantity * item.unit_price for item in order.items.all())
            order.total_amount = total_amount
            order.save()
            
            # Save extended order
            if extended_order:
                extended_form.save()
            else:
                extended_order = extended_form.save(commit=False)
                extended_order.order = order
                
                # Set branch to user's branch if not provided
                if not extended_order.branch:
                    extended_order.branch = request.user.branch
                    
                extended_order.save()
                
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
                            'target_branch': extended_order.branch,
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
        
        if extended_order:
            extended_form = ExtendedOrderForm(instance=extended_order)
        else:
            extended_form = ExtendedOrderForm()
            
            # Set default branch to user's branch
            if not request.user.is_superuser:
                extended_form.fields['branch'].initial = request.user.branch
                extended_form.fields['branch'].queryset = Branch.objects.filter(id=request.user.branch.id)
    
    context = {
        'form': form,
        'formset': formset,
        'extended_form': extended_form,
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

@login_required
def accessory_item_create(request, order_pk):
    """
    View for creating accessory items for an order
    """
    order = get_object_or_404(Order, pk=order_pk)
    
    # Get extended order
    try:
        extended_order = order.extended_info
    except ExtendedOrder.DoesNotExist:
        messages.error(request, 'يجب إنشاء معلومات الطلب الإضافية أولاً.')
        return redirect('orders:order_detail', pk=order.pk)
    
    if request.method == 'POST':
        formset = AccessoryItemFormSet(request.POST, instance=extended_order)
        
        if formset.is_valid():
            formset.save()
            messages.success(request, 'تم حفظ عناصر الاكسسوارات بنجاح.')
            return redirect('orders:order_detail', pk=order.pk)
    else:
        formset = AccessoryItemFormSet(instance=extended_order)
    
    context = {
        'formset': formset,
        'order': order,
        'extended_order': extended_order,
        'title': 'إضافة عناصر اكسسوارات',
    }
    
    return render(request, 'orders/accessory_item_form.html', context)

@login_required
def fabric_order_create(request, order_pk):
    """
    View for creating or updating a fabric order
    """
    order = get_object_or_404(Order, pk=order_pk)
    
    # Get extended order
    try:
        extended_order = order.extended_info
    except ExtendedOrder.DoesNotExist:
        messages.error(request, 'يجب إنشاء معلومات الطلب الإضافية أولاً.')
        return redirect('orders:order_detail', pk=order.pk)
    
    # Get or create fabric order
    try:
        fabric_order = extended_order.fabric_order
    except:
        fabric_order = None
    
    if request.method == 'POST':
        if fabric_order:
            form = FabricOrderForm(request.POST, instance=fabric_order)
        else:
            form = FabricOrderForm(request.POST)
        
        if form.is_valid():
            fabric_order = form.save(commit=False)
            fabric_order.extended_order = extended_order
            fabric_order.save()
            
            # Create inventory supply order notification
            try:
                from accounts.models import Notification, Department
                inventory_dept = Department.objects.filter(code='inventory').first()
                if inventory_dept:
                    # Create notification data
                    notification_data = {
                        'title': 'طلب توريد قماش من المخزن',
                        'message': f'تم إنشاء طلب قماش جديد رقم {order.order_number} - {fabric_order.fabric_type.name} - الكمية: {fabric_order.quantity} {fabric_order.fabric_type.get_unit_display()}',
                        'priority': 'high',
                        'sender': request.user,
                        'target_department': inventory_dept,
                        'target_branch': extended_order.branch,
                        'related_object': order
                    }
                    
                    # Add sender department if exists
                    if hasattr(request.user, 'departments') and request.user.departments.exists():
                        notification_data['sender_department'] = request.user.departments.first()
                    
                    # Create notification
                    Notification.objects.create(**notification_data)
                    
                    # Create a purchase order in inventory if needed
                    from inventory.models import PurchaseOrder, PurchaseOrderItem, Supplier
                    
                    # Get default supplier or create one
                    default_supplier, created = Supplier.objects.get_or_create(
                        name="المورد الافتراضي للأقمشة",
                        defaults={
                            'contact_person': 'مدير المبيعات',
                            'phone': '01000000000',
                            'address': 'عنوان المورد',
                        }
                    )
                    
                    # Create purchase order
                    purchase_order = PurchaseOrder.objects.create(
                        supplier=default_supplier,
                        order_number=f"PO-{order.order_number}",
                        status='ordered',
                        notes=f"طلب توريد قماش لطلب العميل رقم {order.order_number}",
                        created_by=request.user
                    )
                    
                    # Create purchase order item
                    PurchaseOrderItem.objects.create(
                        purchase_order=purchase_order,
                        product=fabric_order.fabric_type,
                        quantity=fabric_order.quantity,
                        unit_price=fabric_order.fabric_type.price
                    )
                    
                    messages.success(request, 'تم إنشاء طلب توريد للمخزن بنجاح.')
            except Exception as e:
                print(f"Error creating inventory supply order: {str(e)}")
                messages.warning(request, 'تم حفظ طلب القماش ولكن حدث خطأ أثناء إنشاء طلب التوريد للمخزن.')
            
            messages.success(request, 'تم حفظ طلب القماش بنجاح.')
            return redirect('orders:order_detail', pk=order.pk)
    else:
        if fabric_order:
            form = FabricOrderForm(instance=fabric_order)
        else:
            form = FabricOrderForm()
    
    context = {
        'form': form,
        'order': order,
        'extended_order': extended_order,
        'fabric_order': fabric_order,
        'title': 'طلب قماش',
    }
    
    return render(request, 'orders/fabric_order_form.html', context)
