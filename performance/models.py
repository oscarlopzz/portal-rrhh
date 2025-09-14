from django.db import models
from django.conf import settings

class Evaluation(models.Model):
    DRAFT = 'DRAFT'
    PENDING = 'PENDING'
    COMPLETED = 'COMPLETED'
    STATUS_CHOICES = [
        (DRAFT, 'Borrador'),
        (PENDING, 'Pendiente revisión'),
        (COMPLETED, 'Completada'),
    ]

    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='evaluations')
    period_start = models.DateField()
    period_end = models.DateField()
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # 0–100.00
    comments = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='evaluations_created')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='evaluations_reviewed')
    reviewed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        permissions = [
            ('can_review_evaluations', 'Puede revisar evaluaciones'),
        ]

    def __str__(self):
        return f"Eval #{self.id} {self.employee} [{self.period_start}–{self.period_end}]"
