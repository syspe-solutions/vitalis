from django.db import models

from apps.common.models import BaseModelAbstract


class BehavioralGoal(BaseModelAbstract):
    """Objetivo/comportamento-alvo acompanhado ao longo das sessões de um paciente."""

    class MeasurementType(models.TextChoices):
        FREQUENCY = "FREQUENCY", "Frequência (nº de ocorrências)"
        DURATION = "DURATION", "Duração (minutos)"
        PERCENTAGE = "PERCENTAGE", "Porcentagem de acertos (tentativas)"
        INTENSITY = "INTENSITY", "Intensidade (escala 1-5)"

    patient = models.ForeignKey(
        "scheduling.Patient",
        on_delete=models.CASCADE,
        related_name="behavioral_goals",
        verbose_name="Paciente",
    )
    title = models.CharField(max_length=150, verbose_name="Objetivo/Comportamento-Alvo")
    description = models.TextField(blank=True, verbose_name="Descrição/Operacionalização")
    measurement_type = models.CharField(
        max_length=20, choices=MeasurementType.choices, verbose_name="Tipo de Medida"
    )
    is_active = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        verbose_name = "Objetivo Comportamental"
        verbose_name_plural = "Objetivos Comportamentais"
        ordering = ["-is_active", "title"]

    def __str__(self) -> str:
        return f"{self.title} ({self.patient.name})"
