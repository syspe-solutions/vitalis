from django.db import models

from apps.common.models import BaseModelAbstract


class BehavioralRecord(BaseModelAbstract):
    """Registro de coleta de dados de um objetivo comportamental, feito em uma sessão."""

    appointment = models.ForeignKey(
        "scheduling.Appointment",
        on_delete=models.CASCADE,
        related_name="behavioral_records",
        verbose_name="Sessão/Agendamento",
    )
    goal = models.ForeignKey(
        "scheduling.BehavioralGoal",
        on_delete=models.CASCADE,
        related_name="records",
        verbose_name="Objetivo",
    )

    value = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Valor (frequência/duração/intensidade)",
    )
    trials_correct = models.PositiveIntegerField(null=True, blank=True, verbose_name="Acertos")
    trials_total = models.PositiveIntegerField(null=True, blank=True, verbose_name="Total de Tentativas")

    notes = models.TextField(blank=True, verbose_name="Observações")

    class Meta:
        verbose_name = "Registro de Coleta"
        verbose_name_plural = "Registros de Coleta"
        ordering = ["-appointment__session_datetime"]

    def __str__(self) -> str:
        return f"{self.goal.title} — {self.appointment.session_datetime:%d/%m/%Y}"

    @property
    def percentage(self):
        if self.trials_total:
            return round((self.trials_correct or 0) / self.trials_total * 100, 1)
        return None

    @property
    def display_value(self):
        if self.goal.measurement_type == self.goal.MeasurementType.PERCENTAGE:
            pct = self.percentage
            if pct is None:
                return "—"
            return f"{self.trials_correct}/{self.trials_total} ({pct}%)"
        if self.value is None:
            return "—"
        unit = {
            self.goal.MeasurementType.FREQUENCY: "x",
            self.goal.MeasurementType.DURATION: "min",
            self.goal.MeasurementType.INTENSITY: "/5",
        }.get(self.goal.measurement_type, "")
        return f"{self.value}{unit}"
