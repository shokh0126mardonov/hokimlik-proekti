# apps/analytics/services/analytics_service.py

from django.db.models import F, ExpressionWrapper, DurationField, Avg, Count
from django.core.cache import cache
from datetime import timedelta

from apps.applications.models import Application


class AnalyticsService:

    CACHE_TIMEOUT = 60 * 5  # 5 min

    # 🔹 REVIEW TIME
    @staticmethod
    def get_avg_review_time():
        return cache.get_or_set("avg_review_time", lambda: (
            Application.objects
            .filter(sent_to_mahalla_at__isnull=False)
            .annotate(
                review_time=ExpressionWrapper(
                    F("sent_to_mahalla_at") - F("created_at"),
                    output_field=DurationField()
                )
            )
            .aggregate(avg=Avg("review_time"))["avg"]
        ), AnalyticsService.CACHE_TIMEOUT)

    # 🔹 EXECUTION TIME
    @staticmethod
    def get_avg_execution_time():
        return cache.get_or_set("avg_execution_time", lambda: (
            Application.objects
            .filter(
                closed_at__isnull=False,
                sent_to_mahalla_at__isnull=False
            )
            .annotate(
                execution_time=ExpressionWrapper(
                    F("closed_at") - F("sent_to_mahalla_at"),
                    output_field=DurationField()
                )
            )
            .aggregate(avg=Avg("execution_time"))["avg"]
        ), AnalyticsService.CACHE_TIMEOUT)

    # 🔹 TOTAL TIME
    @staticmethod
    def get_avg_total_time():
        return cache.get_or_set("avg_total_time", lambda: (
            Application.objects
            .filter(closed_at__isnull=False)
            .annotate(
                total_time=ExpressionWrapper(
                    F("closed_at") - F("created_at"),
                    output_field=DurationField()
                )
            )
            .aggregate(avg=Avg("total_time"))["avg"]
        ), AnalyticsService.CACHE_TIMEOUT)

    # 🔹 BY SERVICE
    @staticmethod
    def get_avg_time_by_service():
        return cache.get_or_set("by_service", lambda: list(
            Application.objects
            .filter(closed_at__isnull=False)
            .annotate(
                total_time=ExpressionWrapper(
                    F("closed_at") - F("created_at"),
                    output_field=DurationField()
                )
            )
            .filter(total_time__lt=timedelta(days=7))
            .values("service__id", "service__name")
            .annotate(
                avg_time=Avg("total_time"),
                count=Count("id")
            )
            .order_by("-avg_time")
        ), AnalyticsService.CACHE_TIMEOUT)

    # 🔹 SLA
    @staticmethod
    def get_sla(days=3):
        qs = (
            Application.objects
            .filter(closed_at__isnull=False)
            .annotate(
                total_time=ExpressionWrapper(
                    F("closed_at") - F("created_at"),
                    output_field=DurationField()
                )
            )
        )

        total = qs.count()
        violations = qs.filter(total_time__gt=timedelta(days=days)).count()

        return {
            "violations": violations,
            "total": total,
            "rate": (violations / total) if total else 0
        }

    # 🔥 SERVICE DETAIL (drill-down)
    @staticmethod
    def get_service_detail(service_id):
        qs = (
            Application.objects
            .filter(service_id=service_id, closed_at__isnull=False)
            .annotate(
                total_time=ExpressionWrapper(
                    F("closed_at") - F("created_at"),
                    output_field=DurationField()
                )
            )
        )

        return {
            "avg_time": qs.aggregate(avg=Avg("total_time"))["avg"],
            "count": qs.count(),
        }

    # 🔥 MAHALLA BOTTLENECK
    @staticmethod
    def get_by_mahalla():
        return list(
            Application.objects
            .filter(closed_at__isnull=False, mahalla__isnull=False)
            .annotate(
                total_time=ExpressionWrapper(
                    F("closed_at") - F("created_at"),
                    output_field=DurationField()
                )
            )
            .values("mahalla__name")
            .annotate(avg_time=Avg("total_time"), count=Count("id"))
            .order_by("-avg_time")
        )

    # 🔥 SLA BREAKERS
    @staticmethod
    def get_sla_breakers(days=3):
        return list(
            Application.objects
            .filter(closed_at__isnull=False)
            .annotate(
                total_time=ExpressionWrapper(
                    F("closed_at") - F("created_at"),
                    output_field=DurationField()
                )
            )
            .filter(total_time__gt=timedelta(days=days))
            .values("id", "service__name", "created_at", "closed_at")
        )