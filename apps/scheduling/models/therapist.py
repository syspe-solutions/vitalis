import uuid

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone


class TherapistManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError("O terapeuta precisa de um email.")
        if not name:
            raise ValueError("O terapeuta precisa de um nome.")

        email = self.normalize_email(email)
        therapist = self.model(email=email, name=name, **extra_fields)
        therapist.set_password(password)
        therapist.save(using=self._db)
        return therapist

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superusuário precisa ter is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superusuário precisa ter is_superuser=True.")

        return self.create_user(email, name, password, **extra_fields)


class Therapist(AbstractBaseUser, PermissionsMixin):
    """Terapeuta: também é o usuário autenticável do sistema (login por email)."""

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)

    name = models.CharField(max_length=150, verbose_name="Nome")
    email = models.EmailField(unique=True, verbose_name="Email")

    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    is_staff = models.BooleanField(default=False, verbose_name="Acesso ao admin")

    created_at = models.DateTimeField(default=timezone.now, editable=False)

    objects = TherapistManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        verbose_name = "Terapeuta"
        verbose_name_plural = "Terapeutas"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def get_full_name(self) -> str:
        return self.name

    def get_short_name(self) -> str:
        return self.name
