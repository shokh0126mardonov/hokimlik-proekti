# apps/dashboard/services.py

from django.db.models import Count, Q
from django.utils import timezone

from apps.applications.models import Application


def get_dashboard_summary():
    today = timezone.now().date()

    base_qs = Application.objects.all()

    stats = base_qs.aggregate(
        total=Count("id"),
        new=Count("id", filter=Q(status="NEW")),
        in_review=Count("id", filter=Q(status="IN_REVIEW")),
        sent=Count("id", filter=Q(status="SENT_TO_MAHALLA")),
        closed=Count("id", filter=Q(status="CLOSED")),
        today=Count("id", filter=Q(created_at__date=today)),
        overdue=Count(
            "id", filter=Q(deadline__lt=today) & ~Q(status__in=["CLOSED", "ARCHIVED"])
        ),
    )

    by_status = list(base_qs.values("status").annotate(count=Count("id")))

    return {
        "jami_murojaatlar": stats["total"],
        "bugungi_murojaatlar": stats["today"],
        "kechikkan_murojaatlar": stats["overdue"],
        "statuslar": {
            "yangi": stats["new"],
            "korib_chiqilmoqda": stats["in_review"],
            "mahallaga_yuborilgan": stats["sent"],
            "yopilgan": stats["closed"],
        },
        "statuslar_boyicha": by_status,
    }
