from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.views import View

from apps.scheduling.models import Therapist


class TherapistListView(View):
    def get(self, request):
        therapists = Therapist.objects.order_by("name")
        return render(request, "scheduling/therapists/list.html", {"therapists": therapists})


class TherapistCreateView(View):
    def get(self, request):
        return render(request, "scheduling/therapists/form.html")

    def post(self, request):
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        password_confirm = request.POST.get("password_confirm", "")

        form_data = {"name": name, "email": email}

        if not all([name, email, password, password_confirm]):
            messages.error(request, "Preencha todos os campos obrigatórios.")
            return render(request, "scheduling/therapists/form.html", form_data)

        if password != password_confirm:
            messages.error(request, "As senhas não coincidem.")
            return render(request, "scheduling/therapists/form.html", form_data)

        if Therapist.objects.filter(email__iexact=email).exists():
            messages.error(request, "Já existe um terapeuta cadastrado com este email.")
            return render(request, "scheduling/therapists/form.html", form_data)

        try:
            validate_password(password)
        except ValidationError as exc:
            for error in exc.messages:
                messages.error(request, error)
            return render(request, "scheduling/therapists/form.html", form_data)

        Therapist.objects.create_user(email=email, name=name, password=password)

        messages.success(request, "Terapeuta cadastrado com sucesso.")
        return redirect("scheduling:therapist_list")
