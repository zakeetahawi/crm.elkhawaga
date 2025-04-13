from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count

from .models import Installation, TransportRequest
from orders.models import Order
from accounts.models import Branch, User

class BranchAccessMixin(UserPassesTestMixin):
    """
    Mixin to check if user has access to the branch data
    """
    def test_func(self):
        # Superusers can access all branches
        if self.request.user.is_superuser:
            return True
        
        # Check if the object has a branch attribute
        if hasattr(self, 'object') and self.object:
            if hasattr(self.object, 'branch'):
                # Main branch users can access all branches
                if self.request.user.branch.is_main_branch:
                    return True
                # Regular users can only access their branch
                return self.object.branch == self.request.user.branch
        
        # For list views, filtering will be applied in get_queryset
        return True

class InstallationListView(LoginRequiredMixin, ListView):
    model = Installation
    template_name = 'installations/installation_list.html'
    context_object_name = 'installations'
    paginate_by = 10
    
    def get_queryset(self):
        # Only show installations with completed manufacturing
        queryset = Installation.objects.filter(order__production_orders__status='completed')
        
        # Filter by branch if user is not from main branch
        if not self.request.user.is_superuser and not self.request.user.branch.is_main_branch:
            queryset = queryset.filter(branch=self.request.user.branch)
        
        # Filter by status if provided
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(customer__name__icontains=search_query) |
                Q(invoice_number__icontains=search_query) |
                Q(notes__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Installation.STATUS_CHOICES
        context['current_status'] = self.request.GET.get('status', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context

class InstallationDetailView(LoginRequiredMixin, BranchAccessMixin, DetailView):
    model = Installation
    template_name = 'installations/installation_detail.html'
    context_object_name = 'installation'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transport_requests'] = self.object.transport_requests.all()
        return context

class InstallationCreateView(LoginRequiredMixin, CreateView):
    model = Installation
    template_name = 'installations/installation_form.html'
    fields = ['order', 'customer', 'branch', 'invoice_number', 'scheduled_date', 'status', 'payment_verified', 'technician', 'notes']
    success_url = reverse_lazy('installations:installation_list')
    
    def form_valid(self, form):
        # Set the created_by field
        form.instance.created_by = self.request.user
        
        # Set branch to user's branch if not provided
        if not form.instance.branch:
            form.instance.branch = self.request.user.branch
        
        # Check if user has permission to create for this branch
        if not self.request.user.is_superuser and not self.request.user.branch.is_main_branch:
            if form.instance.branch != self.request.user.branch:
                messages.error(self.request, _('لا يمكنك إضافة تركيبات لفرع آخر'))
                return self.form_invalid(form)
        
        messages.success(self.request, _('تم إنشاء طلب التركيب بنجاح'))
        return super().form_valid(form)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        
        # Filter orders by branch if user is not from main branch
        if not self.request.user.is_superuser and not self.request.user.branch.is_main_branch:
            form.fields['order'].queryset = Order.objects.filter(customer__branch=self.request.user.branch)
            form.fields['customer'].queryset = self.request.user.branch.customers.all()
            form.fields['branch'].queryset = Branch.objects.filter(id=self.request.user.branch.id)
        
        return form

class InstallationUpdateView(LoginRequiredMixin, BranchAccessMixin, UpdateView):
    model = Installation
    template_name = 'installations/installation_form.html'
    fields = ['order', 'customer', 'branch', 'invoice_number', 'scheduled_date', 'status', 'payment_verified', 'technician', 'notes']
    
    def get_success_url(self):
        return reverse_lazy('installations:installation_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        # Check if user has permission to update for this branch
        if not self.request.user.is_superuser and not self.request.user.branch.is_main_branch:
            if form.instance.branch != self.request.user.branch:
                messages.error(self.request, _('لا يمكنك تعديل تركيبات لفرع آخر'))
                return self.form_invalid(form)
        
        messages.success(self.request, _('تم تحديث طلب التركيب بنجاح'))
        return super().form_valid(form)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        
        # Filter orders by branch if user is not from main branch
        if not self.request.user.is_superuser and not self.request.user.branch.is_main_branch:
            form.fields['order'].queryset = Order.objects.filter(customer__branch=self.request.user.branch)
            form.fields['customer'].queryset = self.request.user.branch.customers.all()
            form.fields['branch'].queryset = Branch.objects.filter(id=self.request.user.branch.id)
        
        return form

class InstallationDeleteView(LoginRequiredMixin, BranchAccessMixin, DeleteView):
    model = Installation
    template_name = 'installations/installation_confirm_delete.html'
    success_url = reverse_lazy('installations:installation_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _('تم حذف طلب التركيب بنجاح'))
        return super().delete(request, *args, **kwargs)

class TransportListView(LoginRequiredMixin, ListView):
    model = TransportRequest
    template_name = 'installations/transport_list.html'
    context_object_name = 'transports'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = TransportRequest.objects.all()
        
        # Filter by branch if user is not from main branch
        if not self.request.user.is_superuser and not self.request.user.branch.is_main_branch:
            queryset = queryset.filter(installation__branch=self.request.user.branch)
        
        # Filter by status if provided
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(installation__customer__name__icontains=search_query) |
                Q(from_location__icontains=search_query) |
                Q(to_location__icontains=search_query) |
                Q(notes__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = TransportRequest.STATUS_CHOICES
        context['current_status'] = self.request.GET.get('status', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context

class TransportDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = TransportRequest
    template_name = 'installations/transport_detail.html'
    context_object_name = 'transport'
    
    def test_func(self):
        # Superusers can access all
        if self.request.user.is_superuser:
            return True
        
        # Main branch users can access all
        if self.request.user.branch.is_main_branch:
            return True
        
        # Regular users can only access their branch
        return self.get_object().installation.branch == self.request.user.branch
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add drivers for the status update form
        context['drivers'] = User.objects.filter(is_active=True)
        return context

class TransportCreateView(LoginRequiredMixin, CreateView):
    model = TransportRequest
    template_name = 'installations/transport_form.html'
    fields = ['installation', 'from_location', 'to_location', 'scheduled_date', 'status', 'driver', 'notes']
    success_url = reverse_lazy('installations:transport_list')
    
    def form_valid(self, form):
        # Set the created_by field
        form.instance.created_by = self.request.user
        
        # Check if user has permission to create for this installation's branch
        if not self.request.user.is_superuser and not self.request.user.branch.is_main_branch:
            if form.instance.installation.branch != self.request.user.branch:
                messages.error(self.request, _('لا يمكنك إضافة طلبات نقل لفرع آخر'))
                return self.form_invalid(form)
        
        messages.success(self.request, _('تم إنشاء طلب النقل بنجاح'))
        return super().form_valid(form)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        
        # Filter installations by branch if user is not from main branch
        if not self.request.user.is_superuser and not self.request.user.branch.is_main_branch:
            form.fields['installation'].queryset = Installation.objects.filter(branch=self.request.user.branch)
        
        return form

class TransportUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = TransportRequest
    template_name = 'installations/transport_form.html'
    fields = ['installation', 'from_location', 'to_location', 'scheduled_date', 'status', 'driver', 'notes']
    
    def get_success_url(self):
        return reverse_lazy('installations:transport_detail', kwargs={'pk': self.object.pk})
    
    def test_func(self):
        # Superusers can access all
        if self.request.user.is_superuser:
            return True
        
        # Main branch users can access all
        if self.request.user.branch.is_main_branch:
            return True
        
        # Regular users can only access their branch
        return self.get_object().installation.branch == self.request.user.branch
    
    def form_valid(self, form):
        # Check if user has permission to update for this installation's branch
        if not self.request.user.is_superuser and not self.request.user.branch.is_main_branch:
            if form.instance.installation.branch != self.request.user.branch:
                messages.error(self.request, _('لا يمكنك تعديل طلبات نقل لفرع آخر'))
                return self.form_invalid(form)
        
        messages.success(self.request, _('تم تحديث طلب النقل بنجاح'))
        return super().form_valid(form)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        
        # Filter installations by branch if user is not from main branch
        if not self.request.user.is_superuser and not self.request.user.branch.is_main_branch:
            form.fields['installation'].queryset = Installation.objects.filter(branch=self.request.user.branch)
        
        return form

class TransportDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = TransportRequest
    template_name = 'installations/transport_confirm_delete.html'
    success_url = reverse_lazy('installations:transport_list')
    
    def test_func(self):
        # Superusers can access all
        if self.request.user.is_superuser:
            return True
        
        # Main branch users can access all
        if self.request.user.branch.is_main_branch:
            return True
        
        # Regular users can only access their branch
        return self.get_object().installation.branch == self.request.user.branch
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _('تم حذف طلب النقل بنجاح'))
        return super().delete(request, *args, **kwargs)

class InstallationDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'installations/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Filter by branch if user is not from main branch
        if not self.request.user.is_superuser and not self.request.user.branch.is_main_branch:
            installations = Installation.objects.filter(
                branch=self.request.user.branch,
                order__production_orders__status='completed'
            )
            transports = TransportRequest.objects.filter(
                installation__branch=self.request.user.branch,
                installation__order__production_orders__status='completed'
            )
        else:
            installations = Installation.objects.filter(order__production_orders__status='completed')
            transports = TransportRequest.objects.filter(installation__order__production_orders__status='completed')
        
        # Installation statistics
        context['total_installations'] = installations.count()
        context['pending_installations'] = installations.filter(status='pending').count()
        context['scheduled_installations'] = installations.filter(status='scheduled').count()
        context['in_progress_installations'] = installations.filter(status='in_progress').count()
        context['completed_installations'] = installations.filter(status='completed').count()
        context['cancelled_installations'] = installations.filter(status='cancelled').count()
        
        # Transport statistics
        context['total_transports'] = transports.count()
        context['pending_transports'] = transports.filter(status='pending').count()
        context['scheduled_transports'] = transports.filter(status='scheduled').count()
        context['in_progress_transports'] = transports.filter(status='in_progress').count()
        context['completed_transports'] = transports.filter(status='completed').count()
        context['cancelled_transports'] = transports.filter(status='cancelled').count()
        
        # Recent installations
        context['recent_installations'] = installations.order_by('-created_at')[:5]
        
        # Recent transports
        context['recent_transports'] = transports.order_by('-created_at')[:5]
        
        return context
