from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from apps.common.admin import BaseModelAdminAbstract
from apps.scheduling.models import (
    Anamnesis,
    Appointment,
    BehavioralGoal,
    BehavioralRecord,
    Patient,
    Therapist,
)


@admin.register(Patient)
class PatientAdmin(BaseModelAdminAbstract):
    list_display = ("name", "email", "birth_date", "created_at")
    search_fields = ("name", "email")
    ordering = ("name",)
    readonly_fields = ("created_at", "created_by", "updated_at", "updated_by")


@admin.register(Therapist)
class TherapistAdmin(UserAdmin):
    model = Therapist
    list_display = ("name", "email", "is_active", "is_staff", "is_superuser")
    list_filter = ("is_active", "is_staff", "is_superuser")
    search_fields = ("name", "email")
    ordering = ("name",)
    readonly_fields = ("last_login", "created_at")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Dados Pessoais", {"fields": ("name",)}),
        (
            "Permissões",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Datas", {"fields": ("last_login", "created_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "name", "password1", "password2", "is_staff", "is_superuser"),
            },
        ),
    )
    filter_horizontal = ("groups", "user_permissions")


@admin.register(Appointment)
class AppointmentAdmin(BaseModelAdminAbstract):
    list_display = (
        "patient",
        "therapist",
        "session_datetime",
        "status_badge",
        "created_at",
    )
    list_filter = ("status", "therapist", "session_datetime")
    search_fields = ("patient__name", "therapist__name")
    autocomplete_fields = ("patient", "therapist")
    ordering = ("-session_datetime",)
    readonly_fields = ("created_at", "created_by", "updated_at", "updated_by")
    actions = ["mark_as_rescheduled", "mark_as_canceled", "mark_as_completed"]

    fieldsets = (
        ("Agendamento", {"fields": ("patient", "therapist", "session_datetime", "status")}),
        ("Detalhes", {"fields": ("notes",)}),
        (
            "Auditoria",
            {
                "fields": ("created_at", "created_by", "updated_at", "updated_by"),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description="Status")
    def status_badge(self, obj):
        colors = {
            Appointment.Status.SCHEDULED: ("#3b82f6", "#fff"),
            Appointment.Status.RESCHEDULED: ("#f59e0b", "#fff"),
            Appointment.Status.COMPLETED: ("#22c55e", "#fff"),
            Appointment.Status.CANCELED: ("#ef4444", "#fff"),
        }
        bg, fg = colors.get(obj.status, ("#6b7280", "#fff"))
        return format_html(
            '<span style="background:{};color:{};padding:2px 10px;border-radius:10px;'
            'font-size:11px;font-weight:600">{}</span>',
            bg, fg, obj.get_status_display(),
        )

    @admin.action(description="Marcar como remarcado")
    def mark_as_rescheduled(self, request, queryset):
        updated = queryset.update(status=Appointment.Status.RESCHEDULED, updated_by=request.user)
        self.message_user(request, f"{updated} agendamento(s) marcado(s) como remarcado.")

    @admin.action(description="Cancelar agendamentos selecionados")
    def mark_as_canceled(self, request, queryset):
        updated = queryset.update(status=Appointment.Status.CANCELED, updated_by=request.user)
        self.message_user(request, f"{updated} agendamento(s) cancelado(s).")

    @admin.action(description="Marcar como concluído")
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status=Appointment.Status.COMPLETED, updated_by=request.user)
        self.message_user(request, f"{updated} agendamento(s) concluído(s).")


@admin.register(Anamnesis)
class AnamnesisAdmin(BaseModelAdminAbstract):
    list_display = ("patient", "diagnosis", "responsible_name", "updated_at")
    search_fields = ("patient__name", "diagnosis", "responsible_name")
    autocomplete_fields = ("patient",)
    readonly_fields = ("created_at", "created_by", "updated_at", "updated_by")


@admin.register(BehavioralGoal)
class BehavioralGoalAdmin(BaseModelAdminAbstract):
    list_display = ("title", "patient", "measurement_type", "is_active")
    list_filter = ("measurement_type", "is_active")
    search_fields = ("title", "patient__name")
    autocomplete_fields = ("patient",)
    readonly_fields = ("created_at", "created_by", "updated_at", "updated_by")


@admin.register(BehavioralRecord)
class BehavioralRecordAdmin(BaseModelAdminAbstract):
    list_display = ("goal", "appointment", "value_display", "created_at")
    list_filter = ("goal__measurement_type",)
    search_fields = ("goal__title", "appointment__patient__name")
    autocomplete_fields = ("appointment", "goal")
    readonly_fields = ("created_at", "created_by", "updated_at", "updated_by")

    @admin.display(description="Valor")
    def value_display(self, obj):
        return obj.display_value
