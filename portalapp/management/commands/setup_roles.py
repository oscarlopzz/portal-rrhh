from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from justifications.models import Justification
from leaves.models import LeaveRequest
from performance.models import Evaluation  # <-- IMPORTANTE


class Command(BaseCommand):
    help = (
        "Crea roles (RRHH, Supervisor, Empleado) y asigna permisos: "
        "revisar justificantes, aprobar ausencias y revisar evaluaciones."
    )

    def handle(self, *args, **options):
        rrhh, _ = Group.objects.get_or_create(name="RRHH")
        supervisor, _ = Group.objects.get_or_create(name="Supervisor")
        empleado, _ = Group.objects.get_or_create(name="Empleado")

        # --- Justificantes ---
        ct_just = ContentType.objects.get_for_model(Justification)
        perm_review_just, _ = Permission.objects.get_or_create(
            codename="can_review_justifications",
            content_type=ct_just,
            defaults={"name": "Puede revisar justificantes"},
        )

        # --- Ausencias ---
        ct_leave = ContentType.objects.get_for_model(LeaveRequest)
        perm_approve_leave, _ = Permission.objects.get_or_create(
            codename="can_approve_leaves",
            content_type=ct_leave,
            defaults={"name": "Puede aprobar ausencias"},
        )

        # --- Evaluaciones ---
        ct_eval = ContentType.objects.get_for_model(Evaluation)
        perm_review_eval, _ = Permission.objects.get_or_create(
            codename="can_review_evaluations",
            content_type=ct_eval,
            defaults={"name": "Puede revisar evaluaciones"},
        )

        rrhh.permissions.add(perm_review_just, perm_approve_leave, perm_review_eval)
        supervisor.permissions.add(perm_review_just, perm_approve_leave, perm_review_eval)

        self.stdout.write(self.style.SUCCESS(
            "Roles actualizados: RRHH y Supervisor con permisos asignados."
        ))
