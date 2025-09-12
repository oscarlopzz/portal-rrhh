from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Justification

@receiver(post_save, sender=Justification)
def sync_leave_on_justification(sender, instance: Justification, created, **kwargs):
    # Si cambia a aprobado/rechazado, marca decided_at y ajusta la Leave
    if instance.status in (Justification.APPROVED, Justification.REJECTED) and not instance.decided_at:
        instance.decided_at = timezone.now()
        instance.save(update_fields=['decided_at'])

    if instance.leave:
        if instance.status == Justification.APPROVED:
            instance.leave.is_justified = True
            instance.leave.justification_note = f"Justificado por justificante #{instance.id}"
        elif instance.status == Justification.REJECTED:
            # si no hay otro aprobado, desmarca
            has_other = instance.leave.justifications.filter(status=Justification.APPROVED).exclude(id=instance.id).exists()
            instance.leave.is_justified = has_other
            if not has_other:
                instance.leave.justification_note = "Sin justificante aprobado"
        instance.leave.save()
