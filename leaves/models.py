from django.db import models

class LeaveRequest(models.Model):
    VACATION = 'VACATION'
    PERMIT = 'PERMIT'
    SICK = 'SICK'
    OTHER = 'OTHER'
    TYPE_CHOICES = [
        (VACATION, 'Vacaciones'),
        (PERMIT, 'Permiso'),
        (SICK, 'Baja médica'),
        (OTHER, 'Otro'),
    ]

    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    STATUS_CHOICES = [
        (PENDING, 'Pendiente'),
        (APPROVED, 'Aprobada'),
        (REJECTED, 'Rechazada'),
    ]

    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='leave_requests')
    ltype = models.CharField(max_length=20, choices=TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)

    # relación con justificantes
    is_justified = models.BooleanField(default=False)
    justification_note = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        permissions = [
            ('can_approve_leaves', 'Puede aprobar ausencias'),
        ]

    def __str__(self):
        return f"[{self.get_ltype_display()}] {self.employee} {self.start_date} - {self.end_date} ({self.get_status_display()})"
