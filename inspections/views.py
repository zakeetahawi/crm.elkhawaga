from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Inspection, InspectionReport, InspectionNotification, InspectionEvaluation
from .forms import InspectionForm, ReportForm, NotificationForm, EvaluationForm

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'inspections/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now()
        
        # Get all inspections for the current user or all if superuser
        if self.request.user.is_superuser:
            inspections = Inspection.objects.all()
        else:
            inspections = Inspection.objects.filter(inspector=self.request.user)
        
        # Count inspections by status
        context['new_inspections_count'] = inspections.filter(status='new').count()
        context['completed_inspections_count'] = inspections.filter(status='completed').count()
        context['in_progress_inspections_count'] = inspections.filter(status='in_progress').count()
        context['overdue_inspections_count'] = inspections.filter(
            status__in=['new', 'in_progress'],
            date__lt=today
        ).count()
        
        # Get recent inspections
        context['recent_inspections'] = inspections.order_by('-created_at')[:10]
        
        return context

class InspectionListView(LoginRequiredMixin, ListView):
    model = Inspection
    template_name = 'inspections/inspection_list.html'
    context_object_name = 'inspections'
    paginate_by = 10

    def get_queryset(self):
        from datetime import timedelta
        from django.utils import timezone
        # إذا كان سوبر يوزر يعرض كل العناصر، وإلا يعرض العناصر الخاصة به
        queryset = Inspection.objects.all() if self.request.user.is_superuser else Inspection.objects.filter(inspector=self.request.user)
        overdue = self.request.GET.get('overdue')
        status = self.request.GET.get('status')
        if overdue == '1':
            now = timezone.now()
            overdue_time = now - timedelta(hours=24)
            queryset = queryset.filter(status='pending', scheduled_date__isnull=True, request_date__lt=overdue_time.date())
        elif status:
            queryset = queryset.filter(status=status)
        return queryset

class InspectionCreateView(LoginRequiredMixin, CreateView):
    model = Inspection
    form_class = InspectionForm
    template_name = 'inspections/inspection_form.html'
    success_url = reverse_lazy('inspections:inspection_list')

    def form_valid(self, form):
        form.instance.inspector = self.request.user
        messages.success(self.request, 'تم إنشاء المعاينة بنجاح')
        return super().form_valid(form)

class InspectionDetailView(LoginRequiredMixin, DetailView):
    model = Inspection
    template_name = 'inspections/inspection_detail.html'
    context_object_name = 'inspection'

class InspectionUpdateView(LoginRequiredMixin, UpdateView):
    model = Inspection
    form_class = InspectionForm
    template_name = 'inspections/inspection_form.html'
    success_url = reverse_lazy('inspections:inspection_list')

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث المعاينة بنجاح')
        return super().form_valid(form)

class InspectionDeleteView(LoginRequiredMixin, DeleteView):
    model = Inspection
    success_url = reverse_lazy('inspections:inspection_list')
    template_name = 'inspections/inspection_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'تم حذف المعاينة بنجاح')
        return super().delete(request, *args, **kwargs)

class EvaluationCreateView(LoginRequiredMixin, CreateView):
    model = InspectionEvaluation
    form_class = EvaluationForm
    template_name = 'inspections/evaluation_form.html'

    def form_valid(self, form):
        inspection = get_object_or_404(Inspection, pk=self.kwargs['inspection_pk'])
        form.instance.inspection = inspection
        form.instance.evaluator = self.request.user
        messages.success(self.request, 'تم إضافة التقييم بنجاح')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('inspections:inspection_detail', kwargs={'pk': self.kwargs['inspection_pk']})

class NotificationListView(LoginRequiredMixin, ListView):
    model = InspectionNotification
    template_name = 'inspections/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 10

    def get_queryset(self):
        return InspectionNotification.objects.filter(
            recipient=self.request.user
        ).order_by('-created_at')

class NotificationCreateView(LoginRequiredMixin, CreateView):
    model = InspectionNotification
    form_class = NotificationForm
    template_name = 'inspections/notification_form.html'

    def form_valid(self, form):
        inspection = get_object_or_404(Inspection, pk=self.kwargs['inspection_pk'])
        form.instance.inspection = inspection
        form.instance.sender = self.request.user
        messages.success(self.request, 'تم إرسال الإشعار بنجاح')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('inspections:inspection_detail', kwargs={'pk': self.kwargs['inspection_pk']})

def mark_notification_read(request, pk):
    notification = get_object_or_404(InspectionNotification, pk=pk)
    if request.user == notification.recipient:
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        messages.success(request, 'تم تحديث حالة الإشعار')
    return redirect('inspections:notification_list')
