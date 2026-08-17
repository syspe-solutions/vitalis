import json
from datetime import datetime

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View

from apps.scheduling.models import Appointment, Patient, Therapist
from apps.scheduling.services.appointment_notification_service import AppointmentNotificationService

_DATETIME_FMT = "%Y-%m-%dT%H:%M"

_STATUS_COLORS = {
    Appointment.Status.SCHEDULED: "#3b82f6",
    Appointment.Status.RESCHEDULED: "#f59e0b",
    Appointment.Status.COMPLETED: "#22c55e",
    Appointment.Status.CANCELED: "#ef4444",
}


class AppointmentListView(View):
    """Tela de agendamento: calendário + lista, com criação e cancelamento."""

    def get(self, request):
        appointments = Appointment.objects.select_related("patient", "therapist").order_by(
            "-session_datetime"
        )

        events = [
            {
                "id": str(appointment.id),
                "title": f"{appointment.patient.name} — {appointment.therapist.name}",
                "start": appointment.session_datetime.isoformat(),
                "backgroundColor": _STATUS_COLORS.get(appointment.status, "#6b7280"),
                "borderColor": _STATUS_COLORS.get(appointment.status, "#6b7280"),
                "extendedProps": {
                    "appointment_id": str(appointment.id),
                    "patient": appointment.patient.name,
                    "therapist": appointment.therapist.name,
                    "status": appointment.status,
                    "status_label": appointment.get_status_display(),
                    "notes": appointment.notes or "—",
                },
            }
            for appointment in appointments
        ]

        return render(request, "scheduling/appointments/list.html", {
            "appointments": appointments,
            "events_json": json.dumps(events, ensure_ascii=False),
            "patients": Patient.objects.order_by("name"),
            "therapists": Therapist.objects.filter(is_active=True).order_by("name"),
            "can_manage": request.user.is_authenticated and request.user.is_superuser,
        })


class AppointmentCreateView(View):
    def get(self, request):
        return render(request, "scheduling/appointments/form.html", self._form_context())

    def post(self, request):
        patient_id = request.POST.get("patient")
        therapist_id = request.POST.get("therapist")
        session_datetime_raw = request.POST.get("session_datetime", "").strip()
        notes = request.POST.get("notes", "").strip() or None

        if not all([patient_id, therapist_id, session_datetime_raw]):
            messages.error(request, "Preencha todos os campos obrigatórios.")
            return render(request, "scheduling/appointments/form.html", self._form_context())

        try:
            patient = Patient.objects.get(pk=patient_id)
        except Patient.DoesNotExist:
            messages.error(request, "Paciente não encontrado.")
            return render(request, "scheduling/appointments/form.html", self._form_context())

        try:
            therapist = Therapist.objects.get(pk=therapist_id)
        except Therapist.DoesNotExist:
            messages.error(request, "Terapeuta não encontrado.")
            return render(request, "scheduling/appointments/form.html", self._form_context())

        try:
            session_datetime = timezone.make_aware(datetime.strptime(session_datetime_raw, _DATETIME_FMT))
        except ValueError:
            messages.error(request, "Data/horário da sessão inválido.")
            return render(request, "scheduling/appointments/form.html", self._form_context())

        created_by = request.user if request.user.is_authenticated else None
        appointment = Appointment.objects.create(
            patient=patient,
            therapist=therapist,
            session_datetime=session_datetime,
            notes=notes,
            created_by=created_by,
            updated_by=created_by,
        )

        AppointmentNotificationService.notify_scheduled(appointment)

        messages.success(request, "Agendamento realizado com sucesso. Notificações enviadas por e-mail.")
        return redirect("scheduling:appointment_list")

    @staticmethod
    def _form_context():
        return {
            "patients": Patient.objects.order_by("name"),
            "therapists": Therapist.objects.filter(is_active=True).order_by("name"),
        }


class AppointmentCancelView(View):
    def post(self, request, pk):
        if not (request.user.is_authenticated and request.user.is_superuser):
            messages.error(request, "Apenas o superusuário pode cancelar agendamentos.")
            return redirect("scheduling:appointment_list")

        appointment = get_object_or_404(Appointment, pk=pk)

        if appointment.status == Appointment.Status.CANCELED:
            messages.warning(request, "Este agendamento já está cancelado.")
            return redirect("scheduling:appointment_list")

        appointment.status = Appointment.Status.CANCELED
        appointment.updated_by = request.user
        appointment.save(update_fields=["status", "updated_by", "updated_at"])

        messages.success(request, "Agendamento cancelado.")
        return redirect("scheduling:appointment_list")
