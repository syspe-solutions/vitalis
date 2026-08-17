from django.db import models

from apps.common.models import BaseModelAbstract


class Patient(BaseModelAbstract):
    name = models.CharField(max_length=150, verbose_name="Nome")
    email = models.EmailField(verbose_name="Email")
    birth_date = models.DateField(verbose_name="Data de Nascimento")

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
