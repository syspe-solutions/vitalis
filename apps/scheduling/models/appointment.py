from django.db import models

from apps.common.models import BaseModelAbstract


class Appointment(BaseModelAbstract):
    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Agendado"
        RESCHEDULED = "RESCHEDULED", "Remarcado"
        COMPLETED = "COMPLETED", "Concluído"
        CANCELED = "CANCELED", "Cancelado"

    patient = models.ForeignKey(
        "scheduling.Patient",
        on_delete=models.CASCADE,
        related_name="appointments",
        verbose_name="Paciente",
    )
    therapist = models.ForeignKey(
        "scheduling.Therapist",
        on_delete=models.PROTECT,
        related_name="appointments",
        verbose_name="Terapeuta",
    )

    session_datetime = models.DateTimeField(verbose_name="Data e Horário da Sessão")

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
        verbose_name="Status",
    )

    notes = models.TextField(blank=True, null=True, verbose_name="Observações")

    class Meta:
        verbose_name = "Agendamento"
        verbose_name_plural = "Agendamentos"
        ordering = ["-session_datetime"]

    def __str__(self) -> str:
        return f"{self.patient.name} com {self.therapist.name} — {self.session_datetime:%d/%m/%Y %H:%M}"
