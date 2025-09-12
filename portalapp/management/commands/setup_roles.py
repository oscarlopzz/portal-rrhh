from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from justifications.models import Justification
from leaves.models import LeaveRequest


class Command(BaseCommand):
    help = "Crea roles (RRHH, Supervisor, Empleado) y asigna permisos de revisión de justificantes y aprobación de ausencias"

    def handle(self, *args, **options):
        rrhh, _ = Group.objects.get_or_create(name="RRHH")
        supervisor, _ = Group.objects.get_or_create(name="Supervisor")
        empleado, _ = Group.objects.get_or_create(name="Empleado")

        # --- Permiso: revisar justificantes ---
        ct_just = ContentType.objects.get_for_model(Justification)
        review_perm, _ = Permission.objects.get_or_create(
            codename="can_review_justifications",
            content_type=ct_just,
            defaults={"name": "Puede revisar justificantes"},
        )

        # --- Permiso: aprobar ausencias ---
        ct_leave = ContentType.objects.get_for_model(LeaveRequest)
        approve_perm, _ = Permission.objects.get_or_create(
            codename="can_approve_leaves",
            content_type=ct_leave,
            defaults={"name": "Puede aprobar ausencias"},
        )

        # Asignar a RRHH y Supervisor
        rrhh.permissions.add(review_perm, approve_perm)
        supervisor.permissions.add(review_perm, approve_perm)

        self.stdout.write(self.style.SUCCESS(
            "Roles actualizados: RRHH y Supervisor con permisos de revisar justificantes y aprobar ausencias."
        ))
