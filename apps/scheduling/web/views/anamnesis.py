from datetime import datetime

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from apps.scheduling.models import Anamnesis, Patient

_DATE_FMT = "%Y-%m-%d"

_TEXT_FIELDS = [
    "chief_complaint",
    "diagnosis",
    "diagnosing_professional",
    "medical_history",
    "family_history",
    "developmental_milestones",
    "communication_profile",
    "sensory_profile",
    "behaviors_of_concern",
    "feeding_notes",
    "sleep_notes",
    "current_medications",
    "previous_therapies",
    "school_info",
    "family_expectations",
    "additional_notes",
]
_REQUIRED_FIELDS = ["responsible_name", "responsible_relationship", "chief_complaint"]


def _values_from_instance(anamnesis):
    if not anamnesis:
        return {}
    values = {
        "responsible_name": anamnesis.responsible_name,
        "responsible_relationship": anamnesis.responsible_relationship,
        "responsible_phone": anamnesis.responsible_phone,
        "diagnosis_date": anamnesis.diagnosis_date.isoformat() if anamnesis.diagnosis_date else "",
    }
    values.update({field: getattr(anamnesis, field) for field in _TEXT_FIELDS})
    return values


def _values_from_post(post):
    values = {
        "responsible_name": post.get("responsible_name", "").strip(),
        "responsible_relationship": post.get("responsible_relationship", "").strip(),
        "responsible_phone": post.get("responsible_phone", "").strip(),
        "diagnosis_date": post.get("diagnosis_date", "").strip(),
    }
    values.update({field: post.get(field, "").strip() for field in _TEXT_FIELDS})
    return values


class AnamnesisFormView(View):
    """Anamnese: formulário único de criação/edição (1 anamnese por paciente)."""

    def get(self, request, patient_pk):
        if not request.user.is_authenticated:
            messages.error(request, "Faça login para acessar a anamnese.")
            return redirect("scheduling:patient_detail", pk=patient_pk)

        patient = get_object_or_404(Patient, pk=patient_pk)
        anamnesis = getattr(patient, "anamnesis", None)
        return render(request, "scheduling/anamnesis/form.html", {
            "patient": patient,
            "anamnesis": anamnesis,
            **_values_from_instance(anamnesis),
        })

    def post(self, request, patient_pk):
        if not request.user.is_authenticated:
            messages.error(request, "Faça login para preencher a anamnese.")
            return redirect("scheduling:patient_detail", pk=patient_pk)

        patient = get_object_or_404(Patient, pk=patient_pk)
        anamnesis = getattr(patient, "anamnesis", None)
        values = _values_from_post(request.POST)

        if not all(values[field] for field in _REQUIRED_FIELDS):
            messages.error(
                request,
                "Preencha os campos obrigatórios: responsável, parentesco e queixa principal.",
            )
            return render(request, "scheduling/anamnesis/form.html", {
                "patient": patient, "anamnesis": anamnesis, **values,
            })

        diagnosis_date = None
        if values["diagnosis_date"]:
            try:
                diagnosis_date = datetime.strptime(values["diagnosis_date"], _DATE_FMT).date()
            except ValueError:
                messages.error(request, "Data do diagnóstico inválida.")
                return render(request, "scheduling/anamnesis/form.html", {
                    "patient": patient, "anamnesis": anamnesis, **values,
                })

        save_values = {**values, "diagnosis_date": diagnosis_date}

        if anamnesis:
            for field, value in save_values.items():
                setattr(anamnesis, field, value)
            anamnesis.updated_by = request.user
            anamnesis.save()
        else:
            Anamnesis.objects.create(
                patient=patient,
                created_by=request.user,
                updated_by=request.user,
                **save_values,
            )

        messages.success(request, "Anamnese salva com sucesso.")
        return redirect("scheduling:patient_detail", pk=patient.pk)
