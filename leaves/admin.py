from django.contrib import admin
from .models import LeaveRequest

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'ltype', 'start_date', 'end_date', 'status', 'is_justified')
    list_filter = ('ltype', 'status', 'is_justified', 'start_date', 'end_date', 'created_at')
    search_fields = ('employee__first_name', 'employee__last_name', 'reason')
    autocomplete_fields = ('employee',)
