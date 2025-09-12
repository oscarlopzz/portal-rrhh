from django.contrib import admin
from .models import Employee

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'department', 'position', 'start_date', 'manager')
    list_filter = ('department', 'position', 'start_date')
    search_fields = ('first_name', 'last_name', 'email')
    autocomplete_fields = ('manager', 'user')
