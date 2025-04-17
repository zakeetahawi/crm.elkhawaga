from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Dashboard
    path('', views.inventory_list, name='inventory_list'),
    
    # Products
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/create/', views.product_create, name='product_create'),
    path('product/<int:pk>/update/', views.product_update, name='product_update'),
    path('product/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('product/<int:product_pk>/transaction/create/', views.transaction_create, name='transaction_create'),
    
    # API endpoints
    path('api/products/<int:pk>/', views.product_api_detail, name='product_api_detail'),
    path('api/products/', views.product_api_list, name='product_api_list'),
]
