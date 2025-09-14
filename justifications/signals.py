# justifications/signals.py
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Justification
from portalapp.notifications import (
    notify_rrhh_justification_submitted,
    notify_employee_justification_decided,
)


@receiver(pre_save, sender=Justification)
def _flag_status_change(sender, instance: Justification, **kwargs):
    """Guarda el estado anterior para saber si cambió tras el save."""
    if instance.pk:
        try:
            old = Justification.objects.only('status').get(pk=instance.pk)
            instance._old_status = old.status
        except Justification.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


def _sync_leave(item: Justification):
    """Actualiza la ausencia enlazada según el estado del justificante."""
    if not item.leave:
        return
    if item.status == Justification.APPROVED:
        item.leave.is_justified = True
        item.leave.justification_note = f"Justificante #{item.id} aprobado"
        item.leave.save(update_fields=['is_justified', 'justification_note'])
    elif item.status == Justification.REJECTED:
        # Solo desmarcar si no existe otro justificante aprobado
        has_other = item.leave.justifications.filter(
            status=Justification.APPROVED
        ).exclude(pk=item.pk).exists()
        if not has_other:
            item.leave.is_justified = False
            item.leave.justification_note = "Sin justificante aprobado"
            item.leave.save(update_fields=['is_justified', 'justification_note'])


@receiver(post_save, sender=Justification)
def _auto_notify_and_sync(sender, instance: Justification, created, **kwargs):
    # 1) Al crear → notifica a RRHH
    if created:
        notify_rrhh_justification_submitted(instance)
        return

    # 2) Si cambió el estado a APROBADO/RECHAZADO → decided_at, sync y notifica empleado
    old = getattr(instance, "_old_status", None)
    if old != instance.status and instance.status in (Justification.APPROVED, Justification.REJECTED):
        if not instance.decided_at:
            instance.decided_at = timezone.now()
            # Este save dispara otro post_save, pero sin cambio de estado → no reenvía
            instance.save(update_fields=['decided_at'])
        _sync_leave(instance)
        notify_employee_justification_decided(instance)
