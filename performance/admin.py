from django.contrib import admin
from .models import Evaluation

@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'period_start', 'period_end', 'score', 'status', 'created_at')
    list_filter = ('status', 'period_start', 'period_end')
    search_fields = ('employee__first_name', 'employee__last_name', 'employee__email')
