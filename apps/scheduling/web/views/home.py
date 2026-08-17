from django.utils import timezone
from django.views.generic import TemplateView

from apps.scheduling.models import Appointment, Patient, Therapist


class HomeView(TemplateView):
    template_name = "scheduling/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["patients_count"] = Patient.objects.count()
        context["therapists_count"] = Therapist.objects.count()
        context["upcoming_appointments"] = (
            Appointment.objects.select_related("patient", "therapist")
            .exclude(status=Appointment.Status.CANCELED)
            .filter(session_datetime__gte=timezone.now())
            .order_by("session_datetime")[:5]
        )
        return context
