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

@login_required
@permission_required('performance.can_review_evaluations', raise_exception=True)
def review_detail(request, pk):
    item = get_object_or_404(Evaluation, pk=pk)
    if request.method == 'POST':
        form = EvaluationReviewForm(request.POST)
        if form.is_valid():
            form.save(reviewer=request.user, instance=item)
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

