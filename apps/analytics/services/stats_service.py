# services/stats_service.py

from django.db.models import Count, Q, Avg, F, ExpressionWrapper, DurationField, Min
from django.db.models.functions import TruncDate
from datetime import timedelta
from django.utils.timezone import now

from apps.applications.models import Application


class StatsService:

    @staticmethod
    def get_base_qs(oqsoqol_id: int):
        """
        Common queryset — DRY principle
        """
        return Application.objects.filter(
            reports__oqsoqol_id=oqsoqol_id
        ).distinct()

    # 🔥 1. STATUS BREAKDOWN (sen so‘ragan qism)
    @staticmethod
    def get_full_status_stats(oqsoqol_id: int):
        qs = StatsService.get_base_qs(oqsoqol_id)

        return qs.aggregate(
            jami_arizalar=Count("id"),

            yangi=Count("id", filter=Q(status=Application.Status.NEW)),
            korib_chiqilmoqda=Count("id", filter=Q(status=Application.Status.IN_REVIEW)),
            mahallaga_yuborilgan=Count("id", filter=Q(status=Application.Status.SENT_TO_MAHALLA)),
            oqsoqol_korgan=Count("id", filter=Q(status=Application.Status.ACKNOWLEDGED)),
            tekshirilgan=Count("id", filter=Q(status=Application.Status.INSPECTED)),
            yopilgan=Count("id", filter=Q(status=Application.Status.CLOSED)),
            arxivlangan=Count("id", filter=Q(status=Application.Status.ARCHIVED)),
            qayta_ochilgan=Count("id", filter=Q(status=Application.Status.REOPENED)),
        )

    # 🔥 2. KPI (high-level stats)
    @staticmethod
    def get_oqsoqol_stats(oqsoqol_id: int):
        qs = StatsService.get_base_qs(oqsoqol_id)

        stats = qs.aggregate(
            total=Count("id"),
            closed=Count("id", filter=Q(status=Application.Status.CLOSED)),
            pending=Count("id", filter=Q(status__in=[
                Application.Status.NEW,
                Application.Status.IN_REVIEW,
                Application.Status.SENT_TO_MAHALLA,
                Application.Status.ACKNOWLEDGED,
                Application.Status.INSPECTED,
            ])),
            rejected=Count("id", filter=Q(status=Application.Status.ARCHIVED)),
        )

        # 🔥 avg response time (NULL-safe)
        qs_with_action = qs.annotate(
            first_action=Min("reports__created_at")
        ).filter(
            first_action__isnull=False,
            sent_to_mahalla_at__isnull=False
        )

        avg_response = qs_with_action.annotate(
            response_time=ExpressionWrapper(
                F("first_action") - F("sent_to_mahalla_at"),
                output_field=DurationField()
            )
        ).aggregate(avg=Avg("response_time"))

        stats["avg_response_time"] = avg_response["avg"]

        return stats

    # 🔥 3. TREND (daily)
    @staticmethod
    def get_trend(oqsoqol_id: int, days: int = 7):
        start = now() - timedelta(days=days)

        qs = (
            StatsService.get_base_qs(oqsoqol_id)
            .filter(created_at__gte=start)
            .annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(count=Count("id", distinct=True))
            .order_by("date")
        )

        return list(qs)

    # 🔥 4. BOTTLENECK ANALYSIS
    @staticmethod
    def get_stage_durations():
        qs = Application.objects.filter(
            sent_to_mahalla_at__isnull=False,
            closed_at__isnull=False
        )

        return qs.annotate(
            review_time=ExpressionWrapper(
                F("sent_to_mahalla_at") - F("created_at"),
                output_field=DurationField()
            ),
            closing_time=ExpressionWrapper(
                F("closed_at") - F("sent_to_mahalla_at"),
                output_field=DurationField()
            )
        ).aggregate(
            avg_review_time=Avg("review_time"),
            avg_closing_time=Avg("closing_time")
        )