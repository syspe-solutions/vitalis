import logging

from django.utils import timezone

from apps.notification.services import EmailService
from apps.scheduling.models import Appointment

logger = logging.getLogger(__name__)

_TEMPLATE = "notification/email/appointment_scheduled.html"
_DATETIME_FMT = "%d/%m/%Y às %H:%M"


class AppointmentNotificationService:
    """Dispara e-mails de confirmação para paciente e terapeuta ao marcar uma sessão.

    Chamada logo após a criação do Appointment; falhas de envio são apenas
    logadas — não devem impedir o agendamento em si de ser concluído.
    """

    @classmethod
    def notify_scheduled(cls, appointment: Appointment) -> None:
        session_fmt = timezone.localtime(appointment.session_datetime).strftime(_DATETIME_FMT)
        base_context = {
            "patient_name": appointment.patient.name,
            "therapist_name": appointment.therapist.name,
            "session_fmt": session_fmt,
            "notes": appointment.notes or "",
        }

        try:
            EmailService.enqueue(
                to=appointment.patient.email,
                subject="Sua sessão foi agendada — Vitalis",
                template=_TEMPLATE,
                recipient_name=appointment.patient.name,
                context_data={
                    **base_context,
                    "heading": "Sessão Agendada",
                    "intro_text": "Sua sessão foi agendada com sucesso. Confira os detalhes abaixo.",
                },
            )
        except Exception:
            logger.exception(
                "Failed to enqueue patient confirmation email for appointment id=%s", appointment.id
            )

        try:
            EmailService.enqueue(
                to=appointment.therapist.email,
                subject="Novo agendamento — Vitalis",
                template=_TEMPLATE,
                recipient_name=appointment.therapist.name,
                context_data={
                    **base_context,
                    "heading": "Novo Agendamento",
                    "intro_text": "Uma nova sessão foi agendada com você. Confira os detalhes abaixo.",
                },
            )
        except Exception:
            logger.exception(
                "Failed to enqueue therapist notification email for appointment id=%s", appointment.id
            )
