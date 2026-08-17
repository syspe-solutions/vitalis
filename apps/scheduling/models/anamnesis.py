from django.db import models

from apps.common.models import BaseModelAbstract


class Anamnesis(BaseModelAbstract):
    """Anamnese: avaliação inicial do paciente, preenchida no início do acompanhamento."""

    patient = models.OneToOneField(
        "scheduling.Patient",
        on_delete=models.CASCADE,
        related_name="anamnesis",
        verbose_name="Paciente",
    )

    # Responsável
    responsible_name = models.CharField(max_length=150, verbose_name="Nome do Responsável")
    responsible_relationship = models.CharField(max_length=100, verbose_name="Parentesco")
    responsible_phone = models.CharField(max_length=30, blank=True, verbose_name="Telefone do Responsável")

    # Diagnóstico
    chief_complaint = models.TextField(verbose_name="Queixa Principal / Motivo da Procura")
    diagnosis = models.CharField(max_length=255, blank=True, verbose_name="Diagnóstico")
    diagnosis_date = models.DateField(null=True, blank=True, verbose_name="Data do Diagnóstico")
    diagnosing_professional = models.CharField(
        max_length=255, blank=True, verbose_name="Profissional/Instituição que Diagnosticou"
    )

    # Histórico
    medical_history = models.TextField(
        blank=True, verbose_name="Histórico Médico (gestação, parto, saúde geral)"
    )
    family_history = models.TextField(blank=True, verbose_name="Histórico Familiar")
    developmental_milestones = models.TextField(
        blank=True, verbose_name="Marcos do Desenvolvimento (motor, fala, social)"
    )

    # Perfil funcional
    communication_profile = models.TextField(
        blank=True, verbose_name="Comunicação (verbal, não-verbal, uso de CAA)"
    )
    sensory_profile = models.TextField(blank=True, verbose_name="Perfil Sensorial")
    behaviors_of_concern = models.TextField(blank=True, verbose_name="Comportamentos de Interesse Clínico")

    # Rotina
    feeding_notes = models.TextField(blank=True, verbose_name="Alimentação")
    sleep_notes = models.TextField(blank=True, verbose_name="Sono")
    current_medications = models.TextField(blank=True, verbose_name="Medicações em Uso")

    # Contexto
    previous_therapies = models.TextField(blank=True, verbose_name="Terapias Anteriores/Atuais")
    school_info = models.TextField(blank=True, verbose_name="Informações Escolares")

    # Expectativas
    family_expectations = models.TextField(blank=True, verbose_name="Expectativas da Família")
    additional_notes = models.TextField(blank=True, verbose_name="Observações Gerais")

    class Meta:
        verbose_name = "Anamnese"
        verbose_name_plural = "Anamneses"

    def __str__(self) -> str:
        return f"Anamnese de {self.patient.name}"
