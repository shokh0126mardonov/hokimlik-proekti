from django.db import models


class Application(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Yangi"
        IN_REVIEW = "in_review", "Hokim ko'rdi"
        SENT_TO_MAHALLA = "sent_to_mahalla", "Mahallaga yuborildi"
        ACKNOWLEDGED = "acknowledged", "Oqsoqol ko'rdi"
        INSPECTED = "inspected", "Tekshirildi"
        CLOSED = "closed", "Yopildi"
        ARCHIVED = "archived", "Arxivlandi"
        REOPENED = "reopened", "Qayta ochildi"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        URGENT = "urgent", "Urgent"

    app_number = models.CharField(
        max_length=30, unique=True, verbose_name="Ariza raqami"
    )

    service = models.ForeignKey(
        "references.Service",
        on_delete=models.PROTECT,
        related_name="applications",
    )

    app_type = models.ForeignKey(
        "references.ApplicationType",
        on_delete=models.PROTECT,
        verbose_name="Murojaat turi",
    )

    content = models.TextField(verbose_name="Murojat")

    citizen_name = models.CharField(max_length=200, verbose_name="Fuqaro F.I.O.")

    citizen_phone = models.CharField(
        max_length=20, null=True, blank=True, verbose_name="Telefon (ixtiyoriy)"
    )

    address_text = models.CharField(max_length=500, verbose_name="Ko'cha va uy raqami")

    mahalla = models.ForeignKey(
        "references.Mahalla",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.NEW,
    )

    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.LOW,
    )

    deadline = models.DateField(null=True, blank=True)

    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_applications",
    )

    reviewed_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_applications",
        verbose_name="Kim ko'rib chiqqani (hokim)",
    )

    sent_to_mahalla_at = models.DateTimeField(null=True, blank=True)

    closed_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Yopilgan vaqt"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Kim kiritgani")

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.pk} {self.app_number}"

    class Meta:
        verbose_name = "Arizalar"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["closed_at"]),
            models.Index(fields=["service"]),
        ]


class MahallaReport(models.Model):
    class ActionType(models.TextChoices):
        ACKNOWLEDGED = "acknowledged", "Qabul qilindi"
        INSPECTED = "inspected", "Tekshirildi"
        COMMENTED = "commented", "Izoh qoldirildi"

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="reports",
    )

    oqsoqol = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="mahalla_reports",
    )

    action_type = models.CharField(
        max_length=20,
        choices=ActionType.choices,
    )

    comment_text = models.TextField(null=True, blank=True)

    telegram_message_id = models.BigIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.oqsoqol.username}"

    class Meta:
        ordering = ["-pk"]


class Attachment(models.Model):
    report = models.ForeignKey(
        MahallaReport,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="attachments",
    )

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="attachments",
    )

    file = models.FileField(upload_to="attachments/")

    file_type = models.CharField(max_length=50)

    file_size = models.IntegerField()

    uploaded_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pk} {self.created_at.strftime('%Y-%m-%d - %H-%M')}"

    class Meta:
        ordering = ["-pk"]
