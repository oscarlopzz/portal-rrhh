from django.db import models
from django.conf import settings

class Justification(models.Model):
    MEDICAL = 'MEDICAL'
    JUDICIAL = 'JUDICIAL'
    OTHER = 'OTHER'
    TYPE_CHOICES = [
        (MEDICAL, 'Médico'),
        (JUDICIAL, 'Judicial'),
        (OTHER, 'Otro'),
    ]

    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    STATUS_CHOICES = [
        (PENDING, 'Pendiente'),
        (APPROVED, 'Aprobado'),
        (REJECTED, 'Rechazado'),
    ]

    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='justifications')
    leave = models.ForeignKey('leaves.LeaveRequest', on_delete=models.SET_NULL, null=True, blank=True, related_name='justifications')

    jtype = models.CharField(max_length=20, choices=TYPE_CHOICES)
    issue_date = models.DateField()
    description = models.TextField(blank=True)
    document = models.FileField(upload_to='justifications/%Y/%m/')  # pdf/jpg/png…

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_justifications')
    created_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        permissions = [
            ('can_review_justifications', 'Puede revisar justificantes'),
        ]

    def __str__(self):
        return f"#{self.id} {self.employee} - {self.get_jtype_display()} - {self.get_status_display()}"
    
    import os  # arriba del archivo o aquí

    @property
    def filename(self):
        return os.path.basename(self.document.name) if self.document else ""

    @property
    def is_image(self):
        name = (self.document.name or "").lower()
        return name.endswith(".jpg") or name.endswith(".jpeg") or name.endswith(".png")

