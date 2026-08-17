import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from apps.notification.models import EmailNotification

logger = logging.getLogger(__name__)


class EmailService:
    """Dispara e-mails de forma síncrona, registrando cada tentativa em EmailNotification.

    Sem fila/Celery: o envio acontece logo após o commit da transação atual (ou
    imediatamente, se não houver transação aberta), sem bloquear a criação do
    registro que originou a notificação em caso de falha de SMTP.
    """

    @classmethod
    def enqueue(
        cls,
        *,
        to: str,
        subject: str,
        template: str,
        recipient_name: str = "",
        context_data: dict | None = None,
    ) -> EmailNotification:
        notification = EmailNotification.objects.create(
            recipient_email=to,
            recipient_name=recipient_name,
            subject=subject,
            template=template,
            context_data=context_data or {},
        )

        notification_pk = str(notification.pk)
        transaction.on_commit(lambda: cls._dispatch(notification_pk))

        logger.info(
            "EmailNotification enqueued id=%s to=%s subject=%r",
            notification_pk, to, subject,
        )
        return notification

    @classmethod
    def _dispatch(cls, notification_pk: str) -> None:
        try:
            notification = EmailNotification.objects.get(pk=notification_pk)
        except EmailNotification.DoesNotExist:
            return

        context = {"notification": notification, **notification.context_data}

        try:
            html_content = render_to_string(notification.template, context)
            text_content = strip_tags(html_content).strip()

            message = EmailMultiAlternatives(
                subject=notification.subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[cls._format_recipient(notification.recipient_email, notification.recipient_name)],
            )
            message.attach_alternative(html_content, "text/html")
            message.send()

            notification.status = EmailNotification.DeliveryStatus.SENT
            notification.sent_at = timezone.now()
            notification.save(update_fields=["status", "sent_at", "updated_at"])

            logger.info("Email dispatched id=%s to=%s", notification.pk, notification.recipient_email)

        except Exception as error:
            notification.status = EmailNotification.DeliveryStatus.FAILED
            notification.last_error = str(error)
            notification.save(update_fields=["status", "last_error", "updated_at"])
            logger.exception("Email dispatch failed id=%s to=%s", notification.pk, notification.recipient_email)

    @staticmethod
    def _format_recipient(email: str, name: str = "") -> str:
        return f"{name} <{email}>" if name else email
