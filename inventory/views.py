from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, F, ExpressionWrapper, DecimalField
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Product, Category, StockTransaction, Supplier, PurchaseOrder

@login_required
def inventory_list(request):
    """
    View for displaying the inventory dashboard
    """
    # Get search and filter parameters
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')
    
    # Get all products
    products = Product.objects.all()
    
    # Apply search filter
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(code__icontains=search_query)
        )
    
    # Apply category filter
    if category_filter:
        products = products.filter(category_id=category_filter)
    
    # Apply status filter
    if status_filter:
        if status_filter == 'low_stock':
            # Products with stock level below minimum
            products = [p for p in products if p.current_stock <= p.minimum_stock and p.current_stock > 0]
        elif status_filter == 'out_of_stock':
            # Products with no stock
            products = [p for p in products if p.current_stock <= 0]
        elif status_filter == 'in_stock':
            # Products with stock level above minimum
            products = [p for p in products if p.current_stock > p.minimum_stock]
    
    # Get all categories for the filter dropdown
    categories = Category.objects.all()
    
    # Calculate inventory statistics
    total_products = Product.objects.count()
    
    # Count low stock products
    low_stock_count = sum(1 for p in Product.objects.all() if p.current_stock <= p.minimum_stock and p.current_stock > 0)
    
    # Count purchase orders
    purchase_orders_count = PurchaseOrder.objects.filter(status='ordered').count()
    
    # Calculate total inventory value
    inventory_value = sum(p.current_stock * p.price for p in Product.objects.all())
    
    # Pagination
    paginator = Paginator(products, 10)  # Show 10 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'إدارة المخزون',
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'status_filter': status_filter,
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'purchase_orders_count': purchase_orders_count,
        'inventory_value': inventory_value,
    }
    return render(request, 'inventory/inventory_list.html', context)

@login_required
def product_detail(request, pk):
    """
    View for displaying product details
    """
    product = get_object_or_404(Product, pk=pk)
    transactions = product.stock_transactions.all().order_by('-date')[:10]
    
    context = {
        'product': product,
        'transactions': transactions,
    }
    return render(request, 'inventory/product_detail.html', context)

@login_required
def product_create(request):
    """
    View for creating a new product
    """
    if request.method == 'POST':
        # Process form data
        name = request.POST.get('name')
        code = request.POST.get('code')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        unit = request.POST.get('unit')
        price = request.POST.get('price')
        minimum_stock = request.POST.get('minimum_stock')
        
        # Validate required fields
        if not name or not code or not category_id or not unit or not price:
            messages.error(request, 'يرجى ملء جميع الحقول المطلوبة')
            return redirect('inventory:product_create')
        
        # Check if code already exists
        if Product.objects.filter(code=code).exists():
            messages.error(request, 'كود المنتج موجود بالفعل')
            return redirect('inventory:product_create')
        
        # Create product
        try:
            category = Category.objects.get(pk=category_id)
            product = Product.objects.create(
                name=name,
                code=code,
                category=category,
                description=description,
                unit=unit,
                price=price,
                minimum_stock=minimum_stock or 0
            )
            messages.success(request, 'تم إنشاء المنتج بنجاح')
            return redirect('inventory:product_detail', pk=product.pk)
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء إنشاء المنتج: {str(e)}')
            return redirect('inventory:product_create')
    
    # GET request
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'unit_choices': Product.UNIT_CHOICES,
    }
    return render(request, 'inventory/product_form.html', context)

@login_required
def product_update(request, pk):
    """
    View for updating a product
    """
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        # Process form data
        name = request.POST.get('name')
        code = request.POST.get('code')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        unit = request.POST.get('unit')
        price = request.POST.get('price')
        minimum_stock = request.POST.get('minimum_stock')
        
        # Validate required fields
        if not name or not code or not category_id or not unit or not price:
            messages.error(request, 'يرجى ملء جميع الحقول المطلوبة')
            return redirect('inventory:product_update', pk=pk)
        
        # Check if code already exists (excluding this product)
        if Product.objects.filter(code=code).exclude(pk=pk).exists():
            messages.error(request, 'كود المنتج موجود بالفعل')
            return redirect('inventory:product_update', pk=pk)
        
        # Update product
        try:
            category = Category.objects.get(pk=category_id)
            product.name = name
            product.code = code
            product.category = category
            product.description = description
            product.unit = unit
            product.price = price
            product.minimum_stock = minimum_stock or 0
            product.save()
            
            messages.success(request, 'تم تحديث المنتج بنجاح')
            return redirect('inventory:product_detail', pk=product.pk)
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء تحديث المنتج: {str(e)}')
            return redirect('inventory:product_update', pk=pk)
    
    # GET request
    categories = Category.objects.all()
    context = {
        'product': product,
        'categories': categories,
        'unit_choices': Product.UNIT_CHOICES,
    }
    return render(request, 'inventory/product_form.html', context)

@login_required
def product_delete(request, pk):
    """
    View for deleting a product
    """
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        try:
            product.delete()
            messages.success(request, 'تم حذف المنتج بنجاح')
            return redirect('inventory:inventory_list')
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء حذف المنتج: {str(e)}')
            return redirect('inventory:product_detail', pk=pk)
    
    context = {
        'product': product,
    }
    return render(request, 'inventory/product_confirm_delete.html', context)

@login_required
def transaction_create(request, product_pk):
    """
    View for creating a stock transaction
    """
    product = get_object_or_404(Product, pk=product_pk)
    
    if request.method == 'POST':
        # Process form data
        transaction_type = request.POST.get('transaction_type')
        reason = request.POST.get('reason')
        quantity = request.POST.get('quantity')
        reference = request.POST.get('reference')
        notes = request.POST.get('notes')
        
        # Validate required fields
        if not transaction_type or not reason or not quantity:
            messages.error(request, 'يرجى ملء جميع الحقول المطلوبة')
            return redirect('inventory:transaction_create', product_pk=product_pk)
        
        # Create transaction
        try:
            quantity = int(quantity)
            if quantity <= 0:
                messages.error(request, 'يجب أن تكون الكمية أكبر من صفر')
                return redirect('inventory:transaction_create', product_pk=product_pk)
            
            # Check if there's enough stock for outgoing transactions
            if transaction_type == 'out' and quantity > product.current_stock:
                messages.error(request, 'الكمية المطلوبة غير متوفرة في المخزون')
                return redirect('inventory:transaction_create', product_pk=product_pk)
            
            transaction = StockTransaction.objects.create(
                product=product,
                transaction_type=transaction_type,
                reason=reason,
                quantity=quantity,
                reference=reference,
                notes=notes,
                created_by=request.user
            )
            
            messages.success(request, 'تم تسجيل حركة المخزون بنجاح')
            return redirect('inventory:product_detail', pk=product_pk)
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء تسجيل حركة المخزون: {str(e)}')
            return redirect('inventory:transaction_create', product_pk=product_pk)
    
    # GET request
    context = {
        'product': product,
        'transaction_types': StockTransaction.TRANSACTION_TYPES,
        'transaction_reasons': StockTransaction.TRANSACTION_REASONS,
    }
    return render(request, 'inventory/transaction_form.html', context)

@login_required
def product_api_detail(request, pk):
    """
    API endpoint for getting product details
    """
    try:
        product = get_object_or_404(Product, pk=pk)
        # Determine product type based on category name
        product_type = 'fabric' if product.category and 'قماش' in product.category.name.lower() else 'accessory'
        
        data = {
            'id': product.id,
            'name': product.name,
            'code': product.code,
            'price': float(product.price),
            'current_stock': product.current_stock,
            'unit': product.unit,
            'product_type': product_type,
        }
        return JsonResponse(data)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def product_api_list(request):
    """
    API endpoint for getting all products with search functionality
    """
    try:
        # Get filter parameters
        category_id = request.GET.get('category', None)
        product_type = request.GET.get('type', None)
        search_query = request.GET.get('search', None)
        
        # Start with all products
        products = Product.objects.all()
        
        # Apply search filter if provided
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) | 
                Q(code__icontains=search_query)
            )
            print(f"Searching for products with query: {search_query}")
        
        # Apply category filter if provided
        if category_id:
            products = products.filter(category_id=category_id)
        
        # Apply product type filter if provided
        if product_type:
            # Filter by product type (fabric or accessory)
            if product_type == 'fabric':
                products = products.filter(category__name__icontains='قماش')
            elif product_type == 'accessory':
                products = products.filter(category__name__icontains='إكسسوار')
        
        # Convert to list of dictionaries
        products_data = []
        for product in products:
            # Determine product type based on category name
            product_type = 'fabric' if product.category and product.category.name and 'قماش' in product.category.name.lower() else 'accessory'
            
            products_data.append({
                'id': product.id,
                'name': product.name,
                'code': product.code,
                'price': float(product.price),
                'current_stock': product.current_stock,
                'unit': product.unit,
                'product_type': product_type,
            })
        
        # Log the number of products being returned
        print(f"Returning {len(products_data)} products")
        
        return JsonResponse(products_data, safe=False)
    except Exception as e:
        print(f"Error in product_api_list: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
