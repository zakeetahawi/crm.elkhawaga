from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone

from .models import (
    Inspection,
    InspectionEvaluation,
    InspectionReport,
    InspectionNotification
)
from .forms import (
    InspectionForm,
    InspectionEvaluationForm,
    InspectionReportForm,
    InspectionNotificationForm,
    InspectionFilterForm
)

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'inspections/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get inspections for the current branch
        branch = self.request.user.branch
        inspections = Inspection.objects.filter(branch=branch)
        
        # Print debug information
        print(f"Dashboard - Found {inspections.count()} inspections for branch {branch}")
        for inspection in inspections:
            print(f"Inspection ID: {inspection.id}, Customer: {inspection.customer}, Status: {inspection.status}")
        
        # Get completed inspections count
        completed_inspections = inspections.filter(status='completed')
        completed_count = completed_inspections.count()
        
        # Statistics
        context['total_inspections'] = inspections.count()
        context['pending_inspections'] = inspections.filter(status='pending').count()
        context['completed_inspections'] = completed_count
        context['success_rate'] = (
            int((completed_inspections.filter(result='passed').count() / completed_count) * 100)
            if completed_count > 0 else 0
        )
        
        # Recent inspections
        context['recent_inspections'] = inspections.order_by('-created_at')[:5]
        
        # Upcoming inspections
        context['upcoming_inspections'] = inspections.filter(
            status='pending',
            scheduled_date__gte=timezone.now().date()
        ).order_by('scheduled_date')[:5]
        
        # Monthly statistics
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        monthly_inspections = inspections.filter(request_date__gte=start_of_month)
        monthly_completed = monthly_inspections.filter(status='completed')
        monthly_completed_count = monthly_completed.count()
        
        context['monthly_stats'] = {
            'total': monthly_inspections.count(),
            'completed': monthly_completed_count,
            'success_rate': (
                int((monthly_completed.filter(result='passed').count() / monthly_completed_count) * 100)
                if monthly_completed_count > 0 else 0
            )
        }
        
        return context

class InspectionListView(LoginRequiredMixin, ListView):
    model = Inspection
    template_name = 'inspections/inspection_list.html'
    context_object_name = 'inspections'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by user's branch
        if not self.request.user.is_superuser:
            queryset = queryset.filter(branch=self.request.user.branch)
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(contract_number__icontains=search) |
                Q(customer__name__icontains=search) |
                Q(notes__icontains=search)
            )
            
        # Status filter
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset.order_by('-request_date')

class InspectionDetailView(LoginRequiredMixin, DetailView):
    model = Inspection
    template_name = 'inspections/inspection_detail.html'
    context_object_name = 'inspection'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get customer notes if customer exists
        if self.object.customer:
            from customers.models import CustomerNote
            customer_notes = CustomerNote.objects.filter(
                customer=self.object.customer
            ).order_by('-created_at')[:5]
            context['customer_notes'] = customer_notes
            
        return context

class InspectionCreateView(LoginRequiredMixin, CreateView):
    model = Inspection
    form_class = InspectionForm
    template_name = 'inspections/inspection_form.html'
    success_url = reverse_lazy('inspections:inspection_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class InspectionUpdateView(LoginRequiredMixin, UpdateView):
    model = Inspection
    form_class = InspectionForm
    template_name = 'inspections/inspection_form.html'
    
    def get_success_url(self):
        return reverse_lazy('inspections:inspection_detail', kwargs={'pk': self.object.pk})

class InspectionDeleteView(LoginRequiredMixin, DeleteView):
    model = Inspection
    template_name = 'inspections/inspection_confirm_delete.html'
    success_url = reverse_lazy('inspections:inspection_list')
    
    def get_queryset(self):
        # Only allow deleting pending inspections
        return super().get_queryset().filter(status='pending')

class EvaluationCreateView(LoginRequiredMixin, CreateView):
    model = InspectionEvaluation
    form_class = InspectionEvaluationForm
    template_name = 'inspections/evaluation_form.html'

    def get_inspection(self):
        return get_object_or_404(Inspection, pk=self.kwargs['inspection_pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['inspection'] = self.get_inspection()
        return context

    def form_valid(self, form):
        form.instance.inspection = self.get_inspection()
        form.instance.created_by = self.request.user
        messages.success(self.request, _('تم إضافة التقييم بنجاح'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('inspections:inspection_detail', kwargs={'pk': self.kwargs['inspection_pk']})

class ReportListView(LoginRequiredMixin, ListView):
    model = InspectionReport
    template_name = 'inspections/report_list.html'
    context_object_name = 'reports'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(branch=self.request.user.branch)
        return queryset.order_by('-created_at')

class ReportDetailView(LoginRequiredMixin, DetailView):
    model = InspectionReport
    template_name = 'inspections/report_detail.html'
    context_object_name = 'report'

class ReportCreateView(LoginRequiredMixin, CreateView):
    model = InspectionReport
    form_class = InspectionReportForm
    template_name = 'inspections/report_form.html'
    success_url = reverse_lazy('inspections:report_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.branch = self.request.user.branch
        report = form.save()
        report.calculate_statistics()
        messages.success(self.request, _('تم إنشاء التقرير بنجاح'))
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if not self.request.user.is_superuser:
            form.fields['branch'].queryset = form.fields['branch'].queryset.filter(
                pk=self.request.user.branch.pk
            )
        return form

class NotificationListView(LoginRequiredMixin, ListView):
    model = InspectionNotification
    template_name = 'inspections/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return InspectionNotification.objects.filter(
            inspection__branch=self.request.user.branch
        ).order_by('-created_at')

class NotificationCreateView(LoginRequiredMixin, CreateView):
    model = InspectionNotification
    form_class = InspectionNotificationForm
    template_name = 'inspections/notification_form.html'

    def get_inspection(self):
        return get_object_or_404(Inspection, pk=self.kwargs['inspection_pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['inspection'] = self.get_inspection()
        return context

    def form_valid(self, form):
        form.instance.inspection = self.get_inspection()
        messages.success(self.request, _('تم إنشاء التنبيه بنجاح'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('inspections:inspection_detail', kwargs={'pk': self.kwargs['inspection_pk']})

def mark_notification_read(request, pk):
    notification = get_object_or_404(InspectionNotification, pk=pk)
    notification.is_read = True
    notification.save()
    return redirect('inspections:notification_list')
