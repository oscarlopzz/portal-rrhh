from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count
import json

from employees.models import Employee
from leaves.models import LeaveRequest
from justifications.models import Justification
from performance.models import Evaluation

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count, Q
from django.utils.dateparse import parse_date
import json

from employees.models import Employee
from leaves.models import LeaveRequest
from justifications.models import Justification
from performance.models import Evaluation


@login_required
def dashboard(request):
    # Filtros (opcionales)
    d_from = parse_date(request.GET.get('from') or '')
    d_to   = parse_date(request.GET.get('to') or '')

    # -------- Leaves (ausencias) con solapamiento de rango ----------
    leaves_qs = LeaveRequest.objects.all()
    if d_from and d_to:
        leaves_qs = leaves_qs.filter(start_date__lte=d_to, end_date__gte=d_from)
    elif d_from:
        leaves_qs = leaves_qs.filter(end_date__gte=d_from)
    elif d_to:
        leaves_qs = leaves_qs.filter(start_date__lte=d_to)

    # -------- Justificantes por fecha de emisión ----------
    just_qs = Justification.objects.all()
    if d_from:
        just_qs = just_qs.filter(issue_date__gte=d_from)
    if d_to:
        just_qs = just_qs.filter(issue_date__lte=d_to)

    # -------- Evaluaciones con solapamiento del periodo ----------
    eval_qs = Evaluation.objects.all()
    if d_from and d_to:
        eval_qs = eval_qs.filter(period_start__lte=d_to, period_end__gte=d_from)
    elif d_from:
        eval_qs = eval_qs.filter(period_end__gte=d_from)
    elif d_to:
        eval_qs = eval_qs.filter(period_start__lte=d_to)

    # KPIs (nota: empleados no se filtra por fecha)
    kpis = {
        'employees_total': Employee.objects.count(),
        'leaves_pending': leaves_qs.filter(status='PENDING').count(),
        'just_pending': just_qs.filter(status='PENDING').count(),
        'evals_pending': eval_qs.filter(status='PENDING').count(),
    }

    # Top 10 departamentos (sin filtro de fecha; puedes adaptarlo si quieres)
    dept_qs = (Employee.objects.values('department')
               .annotate(total=Count('id'))
               .order_by('-total')[:10])
    dept = list(dept_qs)
    dept_labels = [r['department'] or '(Sin asignar)' for r in dept]
    dept_series = [r['total'] for r in dept]

    # Ausencias por estado (filtrado)
    leave_by_status = (leaves_qs.values('status')
                       .annotate(total=Count('id'))
                       .order_by('-total'))
    status_map = dict(LeaveRequest.STATUS_CHOICES)
    leave_labels = [status_map.get(r['status'], r['status']) for r in leave_by_status]
    leave_series = [r['total'] for r in leave_by_status]

    # Justificantes por tipo (filtrado)
    just_by_type = (just_qs.values('jtype')
                    .annotate(total=Count('id'))
                    .order_by('-total'))
    type_map = dict(Justification.TYPE_CHOICES)
    just_labels = [type_map.get(r['jtype'], r['jtype']) for r in just_by_type]
    just_series = [r['total'] for r in just_by_type]

    return render(request, 'reports/dashboard.html', {
        'kpis': kpis,
        'dept': dept,
        'leave_by_status': list(leave_by_status),
        'just_by_type': list(just_by_type),
        # Datos para Chart.js
        'dept_labels': json.dumps(dept_labels),
        'dept_series': json.dumps(dept_series),
        'leave_labels': json.dumps(leave_labels),
        'leave_series': json.dumps(leave_series),
        'just_labels': json.dumps(just_labels),
        'just_series': json.dumps(just_series),
        # Mantener los filtros en el template
        'from': request.GET.get('from', ''),
        'to': request.GET.get('to', ''),
    })
