from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Evaluation
from .forms import EvaluationCreateForm, EvaluationReviewForm

@login_required
def my_evaluations(request):
    employee = getattr(request.user, 'employee_profile', None)
    items = Evaluation.objects.filter(employee=employee).order_by('-created_at') if employee else []
    return render(request, 'performance/my_list.html', {'items': items})

@login_required
@permission_required('performance.can_review_evaluations', raise_exception=True)
def review_list(request):
    status = request.GET.get('status') or ''
    q = request.GET.get('q') or ''
    qs = Evaluation.objects.select_related('employee').order_by('-created_at')
    if status:
        qs = qs.filter(status=status)
    if q:
        qs = qs.filter(
            Q(employee__first_name__icontains=q) |
            Q(employee__last_name__icontains=q) |
            Q(employee__email__icontains=q)
        )
    page = Paginator(qs, 10).get_page(request.GET.get('page'))
    return render(request, 'performance/review_list.html', {'items': page, 'status': status, 'q': q})

@login_required
@permission_required('performance.can_review_evaluations', raise_exception=True)
def create(request):
    if request.method == 'POST':
        form = EvaluationCreateForm(request.POST)
        if form.is_valid():
            ev = form.save(commit=False)
            ev.created_by = request.user
            ev.save()
            messages.success(request, 'Evaluación creada.')
            return redirect('performance_review_list')
    else:
        form = EvaluationCreateForm()
    return render(request, 'performance/create.html', {'form': form})

from django.utils import timezone  # arriba con el resto de imports

from django.utils import timezone  # si no está ya

@login_required
@permission_required('performance.can_review_evaluations', raise_exception=True)
def review_detail(request, pk):
    item = get_object_or_404(Evaluation, pk=pk)

    # por si el modelo usa constante COMPLETED
    STATUS_COMPLETED = getattr(Evaluation, 'COMPLETED', 'COMPLETED')

    if request.method == 'POST':
        # Acción rápida desde el listado o el propio detalle
        action = request.POST.get('action') or request.POST.get('decision')
        if action:  # cualquier valor => completar
            # opcional: si mandas score/comments en el POST, los guardamos
            score = (request.POST.get('score') or '').strip()
            comments = request.POST.get('comments', None)
            if score != '':
                try:
                    item.score = float(score.replace(',', '.'))
                except ValueError:
                    pass
            if comments is not None:
                item.comments = comments

            item.status = STATUS_COMPLETED
            item.reviewer = request.user
            # tu modelo usa reviewed_at (no decided_at) según tu form previo
            if hasattr(item, 'reviewed_at'):
                item.reviewed_at = timezone.now()
                item.save(update_fields=['status', 'reviewer', 'reviewed_at', 'score', 'comments'])
            else:
                item.save(update_fields=['status', 'reviewer', 'score', 'comments'])
            messages.success(request, 'Evaluación completada.')
            return redirect('performance_review_list')

        # Sin acción rápida: procesamos formulario (también completa)
        form = EvaluationReviewForm(request.POST, instance=item)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.status = STATUS_COMPLETED
            obj.reviewer = request.user
            if hasattr(obj, 'reviewed_at'):
                obj.reviewed_at = timezone.now()
            obj.save()
            messages.success(request, 'Evaluación completada.')
            return redirect('performance_review_list')
    else:
        form = EvaluationReviewForm(initial={'score': item.score, 'comments': item.comments})

    return render(request, 'performance/review_detail.html', {'item': item, 'form': form})


@login_required
def performance_home(request):
    # Si puede revisar evaluaciones → lista de revisión
    if request.user.has_perm('performance.can_review_evaluations'):
        return redirect('performance_review_list')
    # Si es empleado con perfil → sus evaluaciones
    if getattr(request.user, 'employee_profile', None):
        return redirect('my_evaluations')
    # Fallback (sin permisos ni perfil)
    return redirect('home')

