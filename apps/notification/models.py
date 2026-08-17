from django.db import models

from apps.common.models import BaseModelAbstract


class EmailNotification(BaseModelAbstract):
    """Registro de e-mail disparado pelo sistema (auditoria + status de entrega)."""

    class DeliveryStatus(models.TextChoices):
        PENDING = "PENDING", "Pendente"
        SENT = "SENT", "Enviado"
        FAILED = "FAILED", "Falhou"

    recipient_email = models.EmailField(verbose_name="Destinatário")
    recipient_name = models.CharField(max_length=150, blank=True, verbose_name="Nome do Destinatário")
    subject = models.CharField(max_length=255, verbose_name="Assunto")
    template = models.CharField(max_length=255, verbose_name="Template")
    context_data = models.JSONField(default=dict, blank=True, verbose_name="Contexto")

    status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.PENDING,
        verbose_name="Status",
    )
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Enviado em")
    last_error = models.TextField(null=True, blank=True, verbose_name="Último Erro")

    class Meta:
        verbose_name = "Notificação por E-mail"
        verbose_name_plural = "Notificações por E-mail"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.subject} → {self.recipient_email} [{self.get_status_display()}]"
