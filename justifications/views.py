from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import JustificationCreateForm, JustificationReviewForm
from .models import Justification
from leaves.models import LeaveRequest

from django.db.models import Q
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.utils import timezone
import csv

@login_required
def home(request):
    """
    Raíz de /justificantes/:
    - Si el usuario puede revisar justificantes (RRHH/Supervisor) -> lista de revisión
    - Si no -> 'Mis justificantes'
    """
    if request.user.has_perm('justifications.can_review_justifications'):
        return redirect('review_list')
    return redirect('my_justifications')


@login_required
def my_justifications(request):
    """
    Listado de justificantes del empleado logueado.
    Requiere que el User esté vinculado a un Employee (employee_profile).
    """
    employee = getattr(request.user, 'employee_profile', None)
    if not employee:
        messages.error(request, "Tu usuario no está vinculado a un empleado.")
        return redirect('home')

    items = (
        Justification.objects
        .filter(employee=employee)
        .select_related('leave')
        .order_by('-created_at')
    )
    return render(request, 'justifications/my_list.html', {'items': items})


@login_required
def create_justification(request):
    """
    Formulario para subir justificantes por el empleado.
    Acepta ?leave=<id> para preseleccionar una ausencia del propio empleado.
    """
    employee = getattr(request.user, 'employee_profile', None)
    if not employee:
        messages.error(request, "Tu usuario no está vinculado a un empleado.")
        return redirect('home')

    # preselección de ausencia por querystring
    preselected_leave = None
    leave_id = request.GET.get('leave')
    if leave_id:
        preselected_leave = LeaveRequest.objects.filter(id=leave_id, employee=employee).first()

    if request.method == 'POST':
        form = JustificationCreateForm(request.POST, request.FILES)
        # Limitar las ausencias del select a las del empleado
        if 'leave' in form.fields:
            form.fields['leave'].queryset = LeaveRequest.objects.filter(employee=employee).order_by('-created_at')

        if form.is_valid():
            j = form.save(commit=False)
            j.employee = employee
            # Si vino preseleccionada por GET y el form no la cambió, respetar
            if preselected_leave and not form.cleaned_data.get('leave'):
                j.leave = preselected_leave
            j.save()
            messages.success(request, "Justificante enviado y pendiente de revisión.")
            return redirect('my_justifications')
    else:
        initial = {'leave': preselected_leave.id} if preselected_leave else {}
        form = JustificationCreateForm(initial=initial)
        if 'leave' in form.fields:
            form.fields['leave'].queryset = LeaveRequest.objects.filter(employee=employee).order_by('-created_at')

    return render(request, 'justifications/create.html', {'form': form})


from django.db.models import Q
from django.core.paginator import Paginator

@login_required
@permission_required('justifications.can_review_justifications', raise_exception=True)
def review_list(request):
    """
    Filtros:
      - ?status=PENDING|APPROVED|REJECTED
      - ?q=texto   (nombre/apellido/email del empleado)
      - ?order=id|employee|jtype|issue_date|status|leave
      - ?dir=asc|desc
      - ?page=N
    """
    status = request.GET.get('status') or ''
    q = request.GET.get('q') or ''
    order = request.GET.get('order') or 'created_at'
    direction = request.GET.get('dir') or 'desc'

    # Mapa de campos permitidos para ordenar
    ordering_map = {
        'id': 'id',
        'employee': 'employee__last_name',
        'jtype': 'jtype',
        'issue_date': 'issue_date',
        'status': 'status',
        'leave': 'leave__id',
        'created_at': 'created_at',
    }
    field = ordering_map.get(order, 'created_at')
    prefix = '' if direction == 'asc' else '-'

    qs = (
        Justification.objects
        .select_related('employee', 'leave')
        .order_by(prefix + field, '-id')  # 2º criterio estable
    )

    if status:
        qs = qs.filter(status=status)

    if q:
        qs = qs.filter(
            Q(employee__first_name__icontains=q) |
            Q(employee__last_name__icontains=q) |
            Q(employee__email__icontains=q)
        )

    paginator = Paginator(qs, 10)  # 10 por página
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(
        request,
        'justifications/review_list.html',
        {
            'items': page_obj,        # Page object
            'status': status,
            'q': q,
            'order': order,
            'dir': direction,
        }
    )


@login_required
@permission_required('justifications.can_review_justifications', raise_exception=True)
def review_detail(request, pk):
    item = get_object_or_404(Justification, pk=pk)

    def _sync_leave(_item):
        if _item.leave:
            if _item.status == Justification.APPROVED:
                _item.leave.is_justified = True
                _item.leave.justification_note = f"Justificante #{_item.id} aprobado"
                _item.leave.save(update_fields=['is_justified', 'justification_note'])
            elif _item.status == Justification.REJECTED:
                # Solo marcar como no justificada si no hay otros aprobados
                approved_exists = _item.leave.justifications.filter(
                    status=Justification.APPROVED
                ).exclude(pk=_item.pk).exists()
                if not approved_exists:
                    _item.leave.is_justified = False
                    _item.leave.save(update_fields=['is_justified'])

    if request.method == 'POST':
        # 1) Acciones rápidas desde la tabla
        decision = request.POST.get('decision')
        if decision in (Justification.APPROVED, Justification.REJECTED):
            item.status = decision
            item.reviewer = request.user
            item.decided_at = timezone.now()
            item.save(update_fields=['status', 'reviewer', 'decided_at'])
            _sync_leave(item)
            messages.success(request, "Decisión registrada.")
            return redirect('review_list')

        # 2) Alternativa: formulario de revisión (si prefieres usarlo)
        form = JustificationReviewForm(request.POST)
        if form.is_valid():
            form.save(reviewer=request.user, instance=item)
            item.decided_at = timezone.now()
            item.save(update_fields=['decided_at'])
            _sync_leave(item)
            messages.success(request, "Decisión registrada.")
            return redirect('review_list')
    else:
        form = JustificationReviewForm()

    return render(request, 'justifications/review_detail.html', {'item': item, 'form': form})

@login_required
@permission_required('justifications.can_review_justifications', raise_exception=True)
def review_export_csv(request):
    status = request.GET.get('status') or ''
    q = request.GET.get('q') or ''
    order = request.GET.get('order') or 'created_at'
    direction = request.GET.get('dir') or 'desc'

    ordering_map = {
        'id': 'id',
        'employee': 'employee__last_name',
        'jtype': 'jtype',
        'issue_date': 'issue_date',
        'status': 'status',
        'leave': 'leave__id',
        'created_at': 'created_at',
    }
    field = ordering_map.get(order, 'created_at')
    prefix = '' if direction == 'asc' else '-'

    qs = (
        Justification.objects
        .select_related('employee', 'leave')
        .order_by(prefix + field, '-id')
    )

    if status:
        qs = qs.filter(status=status)
    if q:
        qs = qs.filter(
            Q(employee__first_name__icontains=q) |
            Q(employee__last_name__icontains=q) |
            Q(employee__email__icontains=q)
        )

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="justificantes.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Empleado', 'Email', 'Tipo', 'Fecha', 'Estado', 'Ausencia', 'Documento'])

    for j in qs:
        writer.writerow([
            j.id,
            str(j.employee) if j.employee_id else '',
            getattr(j.employee, 'email', ''),
            j.get_jtype_display(),
            j.issue_date,
            j.get_status_display(),
            j.leave_id or '',
            j.document.url if j.document else ''
        ])

    return response
