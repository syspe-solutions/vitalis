import json
from datetime import timedelta

from django.contrib import messages
from django.db.models import Count
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views import View

from apps.scheduling.models import Appointment, BehavioralGoal, BehavioralRecord, Patient, Therapist

_STATUS_COLORS = {
    Appointment.Status.SCHEDULED: "#3b82f6",
    Appointment.Status.RESCHEDULED: "#f59e0b",
    Appointment.Status.COMPLETED: "#22c55e",
    Appointment.Status.CANCELED: "#ef4444",
}


class DashboardView(View):
    """Dashboard gerencial: ocupação, taxa de cancelamento e indicadores clínicos agregados."""

    def get(self, request):
        if not (request.user.is_authenticated and request.user.is_superuser):
            messages.error(request, "Apenas o superusuário pode acessar o dashboard gerencial.")
            return redirect("scheduling:home")

        now = timezone.now()
        period_start = now - timedelta(days=30)
        week_end = now + timedelta(days=7)
        today = now.date()

        period_appointments = Appointment.objects.filter(
            session_datetime__gte=period_start, session_datetime__lte=now
        )
        period_total = period_appointments.count()
        canceled_count = period_appointments.filter(status=Appointment.Status.CANCELED).count()
        completed_count = period_appointments.filter(status=Appointment.Status.COMPLETED).count()
        cancellation_rate = round(canceled_count / period_total * 100, 1) if period_total else 0
        completion_rate = round(completed_count / period_total * 100, 1) if period_total else 0

        status_counts = {
            status: period_appointments.filter(status=status).count()
            for status, _ in Appointment.Status.choices
        }

        upcoming_by_therapist = list(
            Appointment.objects.filter(session_datetime__gte=now, session_datetime__lte=week_end)
            .exclude(status=Appointment.Status.CANCELED)
            .values("therapist__name")
            .annotate(total=Count("id"))
            .order_by("-total")
        )

        today_appointments = (
            Appointment.objects.select_related("patient", "therapist")
            .filter(session_datetime__date=today)
            .exclude(status=Appointment.Status.CANCELED)
            .order_by("session_datetime")
        )

        patients_without_anamnesis = Patient.objects.filter(anamnesis__isnull=True).order_by("name")

        context = {
            "patients_count": Patient.objects.count(),
            "active_therapists_count": Therapist.objects.filter(is_active=True).count(),
            "period_total": period_total,
            "cancellation_rate": cancellation_rate,
            "completion_rate": completion_rate,
            "active_goals_count": BehavioralGoal.objects.filter(is_active=True).count(),
            "records_last_30d": BehavioralRecord.objects.filter(created_at__gte=period_start).count(),
            "patients_without_anamnesis": patients_without_anamnesis,
            "today_appointments": today_appointments,
            "status_labels_json": json.dumps(
                [label for _, label in Appointment.Status.choices], ensure_ascii=False
            ),
            "status_values_json": json.dumps(
                [status_counts[status] for status, _ in Appointment.Status.choices]
            ),
            "status_colors_json": json.dumps(
                [_STATUS_COLORS[status] for status, _ in Appointment.Status.choices]
            ),
            "therapist_labels_json": json.dumps(
                [row["therapist__name"] for row in upcoming_by_therapist], ensure_ascii=False
            ),
            "therapist_values_json": json.dumps([row["total"] for row in upcoming_by_therapist]),
        }
        return render(request, "scheduling/dashboard.html", context)
