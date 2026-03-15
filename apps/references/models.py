from django.db import models


class Service(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pk} {self.name}"


class Mahalla(models.Model):
    name = models.CharField(max_length=200)
    district = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pk} {self.name}"


class ApplicationType(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.pk} {self.name}"