from django.db import models


class AuditLog(models.Model):

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    entity_type = models.CharField(max_length=50)

    entity_id = models.CharField()

    action = models.CharField(max_length=50)

    old_data = models.JSONField(null=True, blank=True)

    new_data = models.JSONField(null=True, blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.pk}"