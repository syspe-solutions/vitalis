from datetime import datetime

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from apps.scheduling.models import Patient

_DATE_FMT = "%Y-%m-%d"


def _can_manage(request) -> bool:
    return request.user.is_authenticated and request.user.is_superuser


class PatientListView(View):
    def get(self, request):
        patients = Patient.objects.order_by("name")
        return render(request, "scheduling/patients/list.html", {
            "patients": patients,
            "can_manage": _can_manage(request),
        })


class PatientDetailView(View):
    def get(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk)
        return render(request, "scheduling/patients/detail.html", {
            "patient": patient,
            "can_manage": _can_manage(request),
            "can_view_clinical": request.user.is_authenticated,
        })


class PatientCreateView(View):
    def get(self, request):
        return render(request, "scheduling/patients/form.html")

    def post(self, request):
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        birth_date_raw = request.POST.get("birth_date", "").strip()

        if not all([name, email, birth_date_raw]):
            messages.error(request, "Preencha todos os campos obrigatórios.")
            return render(request, "scheduling/patients/form.html", {
                "name": name, "email": email, "birth_date": birth_date_raw,
            })

        try:
            birth_date = datetime.strptime(birth_date_raw, _DATE_FMT).date()
        except ValueError:
            messages.error(request, "Data de nascimento inválida.")
            return render(request, "scheduling/patients/form.html", {
                "name": name, "email": email, "birth_date": birth_date_raw,
            })

        created_by = request.user if request.user.is_authenticated else None
        Patient.objects.create(
            name=name,
            email=email,
            birth_date=birth_date,
            created_by=created_by,
            updated_by=created_by,
        )

        messages.success(request, "Paciente cadastrado com sucesso.")
        return redirect("scheduling:patient_list")


class PatientUpdateView(View):
    def get(self, request, pk):
        if not _can_manage(request):
            messages.error(request, "Apenas o superusuário pode editar pacientes.")
            return redirect("scheduling:patient_list")

        patient = get_object_or_404(Patient, pk=pk)
        return render(request, "scheduling/patients/form.html", {
            "patient": patient,
            "name": patient.name,
            "email": patient.email,
            "birth_date": patient.birth_date.isoformat(),
        })

    def post(self, request, pk):
        if not _can_manage(request):
            messages.error(request, "Apenas o superusuário pode editar pacientes.")
            return redirect("scheduling:patient_list")

        patient = get_object_or_404(Patient, pk=pk)

        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        birth_date_raw = request.POST.get("birth_date", "").strip()

        if not all([name, email, birth_date_raw]):
            messages.error(request, "Preencha todos os campos obrigatórios.")
            return render(request, "scheduling/patients/form.html", {
                "patient": patient, "name": name, "email": email, "birth_date": birth_date_raw,
            })

        try:
            birth_date = datetime.strptime(birth_date_raw, _DATE_FMT).date()
        except ValueError:
            messages.error(request, "Data de nascimento inválida.")
            return render(request, "scheduling/patients/form.html", {
                "patient": patient, "name": name, "email": email, "birth_date": birth_date_raw,
            })

        patient.name = name
        patient.email = email
        patient.birth_date = birth_date
        patient.updated_by = request.user
        patient.save(update_fields=["name", "email", "birth_date", "updated_by", "updated_at"])

        messages.success(request, "Paciente atualizado com sucesso.")
        return redirect("scheduling:patient_detail", pk=patient.pk)


class PatientDeleteView(View):
    def get(self, request, pk):
        if not _can_manage(request):
            messages.error(request, "Apenas o superusuário pode excluir pacientes.")
            return redirect("scheduling:patient_list")

        patient = get_object_or_404(Patient, pk=pk)
        return render(request, "scheduling/patients/confirm_delete.html", {"patient": patient})

    def post(self, request, pk):
        if not _can_manage(request):
            messages.error(request, "Apenas o superusuário pode excluir pacientes.")
            return redirect("scheduling:patient_list")

        patient = get_object_or_404(Patient, pk=pk)
        patient.delete()

        messages.success(request, "Paciente excluído com sucesso.")
        return redirect("scheduling:patient_list")
