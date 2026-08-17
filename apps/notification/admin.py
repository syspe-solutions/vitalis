from django.contrib import admin
from django.utils.html import format_html

from apps.notification.models import EmailNotification


@admin.register(EmailNotification)
class EmailNotificationAdmin(admin.ModelAdmin):
    list_display = ("subject", "recipient_email", "status_badge", "created_at", "sent_at")
    list_filter = ("status", "created_at")
    search_fields = ("subject", "recipient_email", "recipient_name")
    ordering = ("-created_at",)
    readonly_fields = (
        "recipient_email", "recipient_name", "subject", "template", "context_data",
        "status", "sent_at", "last_error", "created_at", "updated_at",
    )
    list_per_page = 25

    @admin.display(description="Status")
    def status_badge(self, obj):
        colors = {
            EmailNotification.DeliveryStatus.PENDING: ("#f59e0b", "#fff"),
            EmailNotification.DeliveryStatus.SENT: ("#22c55e", "#fff"),
            EmailNotification.DeliveryStatus.FAILED: ("#ef4444", "#fff"),
        }
        bg, fg = colors.get(obj.status, ("#6b7280", "#fff"))
        return format_html(
            '<span style="background:{};color:{};padding:2px 10px;border-radius:10px;'
            'font-size:11px;font-weight:600">{}</span>',
            bg, fg, obj.get_status_display(),
        )

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False
