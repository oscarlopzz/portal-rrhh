from django.contrib import admin
from .models import Employee

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'first_name', 'last_name', 'email',
        'department', 'position', 'start_date',
        'manager', 'user',          # ← aquí añadimos la columna
    )
    list_filter = ('department', 'position', 'start_date', 'user')  # puedes filtrar por user también
    search_fields = (
        'first_name', 'last_name', 'email',
        'user__username', 'user__email',      # ← búsqueda por usuario
    )
    autocomplete_fields = ('manager', 'user')
    list_select_related = ('manager', 'user')  # rendimiento en listas grandes
    ordering = ('last_name', 'first_name')
