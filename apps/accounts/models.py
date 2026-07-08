from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    class Role(models.TextChoices):
        SUPER_ADMIN = "super_admin", "Super Admin"
        SERVICE_STAFF = "service_staff", "Service Staff"
        HOKIM = "hokim", "Hokim"
        OQSOQOL = "oqsoqol", "Oqsoqol"

    full_name = models.CharField(max_length=200)
    phone = PhoneNumberField(unique=True)

    role = models.CharField(max_length=20, choices=Role.choices)


    service = models.ForeignKey(
        "references.Service",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )

    mahalla = models.ForeignKey(
        "references.Mahalla",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )

    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)
    is_active = models.BooleanField(default=True, verbose_name="Faolligi")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pk} {self.username}"

    @property
    def super_admin(self):
        return self.role == self.Role.SUPER_ADMIN

    @property
    def service_staff(self):
        return self.role == self.Role.SERVICE_STAFF

    @property
    def hokim(self):
        return self.role == self.Role.HOKIM

    @property
    def oqsoqol(self):
        return self.role == self.Role.OQSOQOL

    class Meta:
        verbose_name = "Accountlar"
        ordering = ["-pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["role"],
                condition=Q(role__in=["super_admin", "hokim"]),
                name="unique_super_admin_hokim",
            )
        ]


class Applicant(models.Model):
    class AgeAverage(models.TextChoices):
        UTTIZDAN_KATTA = '30_plus', '30 yoshdan katta'
        UTTIZDAN_KICHIK = '30_minus', '30 yoshdan kichik'

    age_medium = models.CharField(
        max_length=20,
        choices=AgeAverage.choices,
        default=AgeAverage.UTTIZDAN_KICHIK
    )

    full_name = models.CharField(
        max_length=128
    )

    phone = PhoneNumberField(unique=True)
    
    # Agar bitta mahalladan ko'plab arizachilar bo'lishi mumkin bo'lsa, unique=True olib tashlanadi
    mahalla = models.ForeignKey(
        'references.Mahalla',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    text = models.TextField()

    def __str__(self):
        return self.full_name