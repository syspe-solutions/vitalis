import json
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from apps.scheduling.models import Appointment, BehavioralGoal, BehavioralRecord, Patient


def _can_view_clinical(request) -> bool:
    return request.user.is_authenticated


class BehavioralGoalCreateView(View):
    def get(self, request, patient_pk):
        if not _can_view_clinical(request):
            messages.error(request, "Faça login para cadastrar objetivos comportamentais.")
            return redirect("scheduling:patient_detail", pk=patient_pk)

        patient = get_object_or_404(Patient, pk=patient_pk)
        return render(request, "scheduling/behavioral/goal_form.html", {
            "patient": patient,
            "measurement_types": BehavioralGoal.MeasurementType.choices,
        })

    def post(self, request, patient_pk):
        if not _can_view_clinical(request):
            messages.error(request, "Faça login para cadastrar objetivos comportamentais.")
            return redirect("scheduling:patient_detail", pk=patient_pk)

        patient = get_object_or_404(Patient, pk=patient_pk)
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        measurement_type = request.POST.get("measurement_type", "").strip()

        if not title or measurement_type not in BehavioralGoal.MeasurementType.values:
            messages.error(request, "Informe o objetivo e um tipo de medida válido.")
            return render(request, "scheduling/behavioral/goal_form.html", {
                "patient": patient,
                "measurement_types": BehavioralGoal.MeasurementType.choices,
                "title": title,
                "description": description,
                "measurement_type": measurement_type,
            })

        BehavioralGoal.objects.create(
            patient=patient,
            title=title,
            description=description,
            measurement_type=measurement_type,
            created_by=request.user,
            updated_by=request.user,
        )

        messages.success(request, "Objetivo comportamental cadastrado.")
        return redirect("scheduling:patient_detail", pk=patient.pk)


class BehavioralGoalDetailView(View):
    """Histórico de coleta de um objetivo + formulário para novo registro."""

    def get(self, request, pk):
        if not _can_view_clinical(request):
            messages.error(request, "Faça login para acessar os dados de coleta.")
            return redirect("scheduling:home")

        goal = get_object_or_404(BehavioralGoal, pk=pk)
        appointments = Appointment.objects.filter(patient=goal.patient).order_by("-session_datetime")
        records = goal.records.select_related("appointment").all()
        records_asc = sorted(records, key=lambda r: r.appointment.session_datetime)

        is_percentage = goal.measurement_type == BehavioralGoal.MeasurementType.PERCENTAGE
        chart_values = [
            float(record.percentage) if is_percentage else float(record.value)
            for record in records_asc
            if (record.percentage if is_percentage else record.value) is not None
        ]
        chart_labels = [
            record.appointment.session_datetime.strftime("%d/%m")
            for record in records_asc
            if (record.percentage if is_percentage else record.value) is not None
        ]
        chart_axis_label = "% de acertos" if is_percentage else goal.get_measurement_type_display()

        return render(request, "scheduling/behavioral/goal_detail.html", {
            "goal": goal,
            "records": records,
            "appointments": appointments,
            "chart_labels_json": json.dumps(chart_labels, ensure_ascii=False),
            "chart_values_json": json.dumps(chart_values),
            "chart_axis_label": chart_axis_label,
        })


class BehavioralRecordCreateView(View):
    def post(self, request, goal_pk):
        if not _can_view_clinical(request):
            messages.error(request, "Faça login para registrar a coleta.")
            return redirect("scheduling:home")

        goal = get_object_or_404(BehavioralGoal, pk=goal_pk)
        appointment_id = request.POST.get("appointment")
        notes = request.POST.get("notes", "").strip()

        try:
            appointment = Appointment.objects.get(pk=appointment_id, patient=goal.patient)
        except (Appointment.DoesNotExist, ValueError, TypeError):
            messages.error(request, "Selecione uma sessão válida deste paciente.")
            return redirect("scheduling:behavioral_goal_detail", pk=goal.pk)

        value = None
        trials_correct = None
        trials_total = None

        if goal.measurement_type == BehavioralGoal.MeasurementType.PERCENTAGE:
            try:
                trials_correct = int(request.POST.get("trials_correct", ""))
                trials_total = int(request.POST.get("trials_total", ""))
            except ValueError:
                messages.error(request, "Informe acertos e total de tentativas.")
                return redirect("scheduling:behavioral_goal_detail", pk=goal.pk)
            if trials_total <= 0 or trials_correct < 0 or trials_correct > trials_total:
                messages.error(request, "Acertos e total de tentativas inválidos.")
                return redirect("scheduling:behavioral_goal_detail", pk=goal.pk)
        else:
            try:
                value = Decimal(request.POST.get("value", "").replace(",", "."))
            except (InvalidOperation, AttributeError):
                messages.error(request, "Informe um valor numérico válido.")
                return redirect("scheduling:behavioral_goal_detail", pk=goal.pk)

        BehavioralRecord.objects.create(
            appointment=appointment,
            goal=goal,
            value=value,
            trials_correct=trials_correct,
            trials_total=trials_total,
            notes=notes,
            created_by=request.user,
            updated_by=request.user,
        )

        messages.success(request, "Registro de coleta salvo.")
        return redirect("scheduling:behavioral_goal_detail", pk=goal.pk)
