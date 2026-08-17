from django.contrib import admin


class BaseModelAdminAbstract(admin.ModelAdmin):
    """ModelAdmin base: preenche created_by/updated_by automaticamente."""

    list_per_page = 25

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
