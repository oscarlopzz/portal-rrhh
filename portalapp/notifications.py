# portalapp/notifications.py
from typing import Iterable
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
from django.contrib.auth.models import Group


def _group_emails(group_name: str) -> list[str]:
    try:
        g = Group.objects.get(name=group_name)
    except Group.DoesNotExist:
        return []
    return [u.email for u in g.user_set.all() if getattr(u, "email", "")]


def _user_email(user) -> list[str]:
    email = getattr(user, "email", "")
    return [email] if email else []


def _render_safe(path: str, ctx: dict, default: str = "") -> str:
    """Renderiza una plantilla; si no existe, devuelve un texto por defecto."""
    try:
        return render_to_string(path, ctx)
    except TemplateDoesNotExist:
        return default or ""


def _send_email(subject: str, to: Iterable[str], template_base: str, context: dict):
    """
    Envía email con versión texto y HTML a partir de:
      - emails/{template_base}.txt
      - emails/{template_base}.html
    """
    to = [e for e in (to or []) if e]
    if not to:
        return

    ctx = {
        **context,
        "SITE_URL": getattr(settings, "SITE_URL", "http://127.0.0.1:8000"),
        "LOGO_URL": getattr(settings, "EMAIL_LOGO_URL", ""),
    }

    # Texto plano (fallback si faltan plantillas)
    text_body = _render_safe(
        f"emails/{template_base}.txt",
        ctx,
        "Notificación del portal RRHH."
    )

    # HTML (si falta, usamos el texto plano envuelto)
    html_body = _render_safe(
        f"emails/{template_base}.html",
        ctx,
        f"<pre style='white-space:pre-wrap'>{text_body}</pre>"
    )

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@portal-rrhh.local"),
        to=list(to),
    )
    if html_body.strip():
        msg.attach_alternative(html_body, "text/html")
    msg.send(fail_silently=True)


# --------- Notificaciones de JUSTIFICANTES ---------

def notify_rrhh_justification_submitted(just):
    subject = f"[RRHH] Nuevo justificante #{just.id} de {just.employee}"
    to = _group_emails("RRHH")
    ctx = {"j": just, "review_url": f"{getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')}/justificantes/revisar/"}
    _send_email(subject, to, "justification_submitted", ctx)


def notify_employee_justification_decided(just):
    user = getattr(just.employee, "user", None)
    to = _user_email(user)
    if not to:
        return
    subject = f"[RRHH] Tu justificante #{just.id} fue {just.get_status_display()}"
    ctx = {"j": just}
    _send_email(subject, to, "justification_decided", ctx)


# --------- Notificaciones de AUSENCIAS ---------

def notify_rrhh_leave_submitted(leave):
    subject = f"[RRHH] Nueva ausencia #{leave.id} de {leave.employee}"
    to = _group_emails("RRHH")
    ctx = {"l": leave, "review_url": f"{getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')}/leaves/revisar/"}
    _send_email(subject, to, "leave_submitted", ctx)


def notify_employee_leave_decided(leave):
    user = getattr(leave.employee, "user", None)
    to = _user_email(user)
    if not to:
        return
    subject = f"[RRHH] Tu ausencia #{leave.id} fue {leave.get_status_display()}"
    ctx = {
        "l": leave,                      # clave original
        "leave": leave,                  # alias para tus plantillas
        "my_list_url": f"{getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')}/leaves/mis/",
    }
    _send_email(subject, to, "leave_decided", ctx)

