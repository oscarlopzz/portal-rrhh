from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count, Q

from employees.models import Employee
from leaves.models import LeaveRequest
from justifications.models import Justification
from performance.models import Evaluation

@login_required
def dashboard(request):
    # KPIs
    kpis = {
        'employees_total': Employee.objects.count(),
        'leaves_pending': LeaveRequest.objects.filter(status='PENDING').count(),
        'just_pending': Justification.objects.filter(status='PENDING').count(),
        'evals_pending': Evaluation.objects.filter(status='PENDING').count(),
    }

    # Distribución por departamento (top 10)
    dept = (Employee.objects.values('department')
            .annotate(total=Count('id')).order_by('-total')[:10])

    # Ausencias por estado
    leave_by_status = (LeaveRequest.objects
                       .values('status')
                       .annotate(total=Count('id'))
                       .order_by('-total'))

    # Justificantes por tipo
    just_by_type = (Justification.objects
                    .values('jtype')
                    .annotate(total=Count('id'))
                    .order_by('-total'))

    return render(request, 'reports/dashboard.html', {
        'kpis': kpis,
        'dept': dept,
        'leave_by_status': leave_by_status,
        'just_by_type': just_by_type,
    })
