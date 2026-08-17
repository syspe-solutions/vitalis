from django.urls import path

from apps.scheduling.web.views.appointments import (
    AppointmentCancelView,
    AppointmentCreateView,
    AppointmentListView,
)
from apps.scheduling.web.views.home import HomeView
from apps.scheduling.web.views.patients import (
    PatientCreateView,
    PatientDeleteView,
    PatientDetailView,
    PatientListView,
    PatientUpdateView,
)
from apps.scheduling.web.views.therapists import TherapistCreateView, TherapistListView

app_name = "scheduling"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("pacientes/", PatientListView.as_view(), name="patient_list"),
    path("pacientes/novo/", PatientCreateView.as_view(), name="patient_create"),
    path("pacientes/<uuid:pk>/", PatientDetailView.as_view(), name="patient_detail"),
    path("pacientes/<uuid:pk>/editar/", PatientUpdateView.as_view(), name="patient_update"),
    path("pacientes/<uuid:pk>/excluir/", PatientDeleteView.as_view(), name="patient_delete"),
    path("terapeutas/", TherapistListView.as_view(), name="therapist_list"),
    path("terapeutas/novo/", TherapistCreateView.as_view(), name="therapist_create"),
    path("agendamentos/", AppointmentListView.as_view(), name="appointment_list"),
    path("agendamentos/novo/", AppointmentCreateView.as_view(), name="appointment_create"),
    path("agendamentos/<uuid:pk>/cancelar/", AppointmentCancelView.as_view(), name="appointment_cancel"),
]
