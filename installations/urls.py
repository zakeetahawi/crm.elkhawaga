from django.urls import path
from . import views

app_name = 'installations'

urlpatterns = [
    # Installation views
    path('', views.InstallationListView.as_view(), name='installation_list'),
    path('create/', views.InstallationCreateView.as_view(), name='installation_create'),
    path('<int:pk>/', views.InstallationDetailView.as_view(), name='installation_detail'),
    path('<int:pk>/update/', views.InstallationUpdateView.as_view(), name='installation_update'),
    path('<int:pk>/delete/', views.InstallationDeleteView.as_view(), name='installation_delete'),
    
    # Transport views
    path('transport/', views.TransportListView.as_view(), name='transport_list'),
    path('transport/create/', views.TransportCreateView.as_view(), name='transport_create'),
    path('transport/<int:pk>/', views.TransportDetailView.as_view(), name='transport_detail'),
    path('transport/<int:pk>/update/', views.TransportUpdateView.as_view(), name='transport_update'),
    path('transport/<int:pk>/delete/', views.TransportDeleteView.as_view(), name='transport_delete'),
    
    # Dashboard
    path('dashboard/', views.InstallationDashboardView.as_view(), name='dashboard'),
]
