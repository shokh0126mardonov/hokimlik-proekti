from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .services.stats_service import StatsService
from .services.insight_service import InsightService
from .services.forecast_service import ForecastService
from .serializers import AnalyticsSerializer
from .permissions import StatisticPermissions




class AnalyticsAPIView(APIView):
    permission_classes = [IsAuthenticated,StatisticPermissions]

    def get(self, request, oqsoqol_id):

        stats = StatsService.get_oqsoqol_stats(oqsoqol_id)
        trend = StatsService.get_trend(oqsoqol_id)

        forecast = ForecastService.forecast()

        insight = InsightService.oqsoqol_insight(stats)

        bottleneck_data = StatsService.get_stage_durations()
        bottleneck = InsightService.bottleneck_insight(bottleneck_data)

        data = {
            **stats,
            "trend": trend,
            "forecast": forecast,
            "insight": insight,
            "bottleneck": bottleneck
        }

        serializer = AnalyticsSerializer(data)
        return Response(serializer.data)



# apps/analytics/views.py

from rest_framework.views import APIView
from rest_framework.response import Response

from apps.analytics.services.analytics_service import AnalyticsService
from apps.analytics.services.ai_service import AIService

def format_duration(td):
    if not td:
        return None
    s = int(td.total_seconds())
    return f"{s//86400} kun {(s%86400)//3600} soat {(s%3600)//60} daqiqa"


class AIInsightsAPIView(APIView):
    permission_classes = [IsAuthenticated,StatisticPermissions]

    def get(self, request):
        avg_review = AnalyticsService.get_avg_review_time()
        avg_execution = AnalyticsService.get_avg_execution_time()
        avg_total = AnalyticsService.get_avg_total_time()

        by_service = AnalyticsService.get_avg_time_by_service()
        sla = AnalyticsService.get_sla()

        # 🔹 METRIKALAR
        metrikalar = {
            "korib_chiqish_vaqti": format_duration(avg_review),
            "bajarilish_vaqti": format_duration(avg_execution),
            "umumiy_vaqt": format_duration(avg_total),
        }

        # 🔹 SERVICE LIST (transform)
        xizmatlar = [
            {
                "xizmat_id": item["service__id"],
                "xizmat_nomi": item["service__name"],
                "orta_vaqt": format_duration(item["avg_time"]),
                "soni": item["count"]
            }
            for item in by_service
        ]

        # 🔹 SLA
        sla_data = {
            "buzilganlar_soni": sla["violations"],
            "jami": sla["total"],
            "foiz": round(sla["rate"] * 100, 1)
        }

        # 🔹 AI
        insight = AIService.generate_insight(metrikalar, by_service, sla)

        return Response({
            "metrikalar": metrikalar,
            "xizmatlar": xizmatlar,
            "sla": sla_data,
            "ai_xulosa": insight
        })
    


# 🔥 SERVICE DETAIL
class ServiceDetailAPIView(APIView):
    permission_classes = [IsAuthenticated,StatisticPermissions]

    def get(self, request, service_id):
        data = AnalyticsService.get_service_detail(service_id)

        return Response({
            "orta_vaqt": format_duration(data["avg_time"]),
            "arizalar_soni": data["count"]
        })


# 🔥 MAHALLA
class MahallaAnalyticsAPIView(APIView):
    permission_classes = [IsAuthenticated,StatisticPermissions]

    def get(self, request):
        data = AnalyticsService.get_by_mahalla()

        result = [
            {
                "mahalla": item["mahalla__name"],
                "orta_vaqt": format_duration(item["avg_time"]),
                "soni": item["count"]
            }
            for item in data
        ]

        return Response(result)


# 🔥 SLA BREAKERS
class SLABreakersAPIView(APIView):
    permission_classes = [IsAuthenticated,StatisticPermissions]

    def get(self, request):
        data = AnalyticsService.get_sla_breakers()

        result = [
            {
                "ariza_id": item["id"],
                "xizmat": item["service__name"],
                "yaratilgan_vaqt": item["created_at"],
                "yopilgan_vaqt": item["closed_at"]
            }
            for item in data
        ]

        return Response(result)