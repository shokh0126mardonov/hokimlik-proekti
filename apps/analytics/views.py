from rest_framework.views import APIView
from rest_framework.response import Response

from .services.stats_service import StatsService
from .services.insight_service import InsightService
from .services.forecast_service import ForecastService
from .serializers import AnalyticsSerializer


class AnalyticsAPIView(APIView):

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