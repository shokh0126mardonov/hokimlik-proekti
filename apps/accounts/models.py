from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q


class User(AbstractUser):
    class Role(models.TextChoices):
        SUPER_ADMIN = "super_admin", "Super Admin"
        SERVICE_STAFF = "service_staff", "Service Staff"
        HOKIM = "hokim", "Hokim"
        OQSOQOL = "oqsoqol", "Oqsoqol"

    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True,null=True,unique=True)

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
    is_active = models.BooleanField(default=True,verbose_name="Faolligi")
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
        ordering = ['-pk']
        constraints = [
            models.UniqueConstraint(
                fields=["role"],
                condition=Q(role="super_admin"),
                name="unique_super_admin"
            )
        ]