from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from justifications.models import Justification

class Command(BaseCommand):
    help = "Crea roles básicos (RRHH, Supervisor, Empleado) y asigna permiso para revisar justificantes"

    def handle(self, *args, **options):
        rrhh, _ = Group.objects.get_or_create(name="RRHH")
        supervisor, _ = Group.objects.get_or_create(name="Supervisor")
        empleado, _ = Group.objects.get_or_create(name="Empleado")

        ct = ContentType.objects.get_for_model(Justification)
        review_perm, _ = Permission.objects.get_or_create(
            codename="can_review_justifications",
            name="Puede revisar justificantes",
            content_type=ct,
        )

        rrhh.permissions.add(review_perm)
        supervisor.permissions.add(review_perm)

        print("Roles creados y permiso asignado a RRHH y Supervisor")
