from django.contrib import admin
from .models import Justification

@admin.register(Justification)
class JustificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'jtype', 'issue_date', 'status', 'leave', 'created_at')
    list_filter = ('jtype', 'status', 'issue_date', 'created_at')
    search_fields = ('employee__first_name', 'employee__last_name', 'description')
    autocomplete_fields = ('employee', 'leave', 'reviewer')
