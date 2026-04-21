from django.urls import path
from .views import AnalyticsAPIView

urlpatterns = [
    path("analytics/oqsoqol/<int:oqsoqol_id>/", AnalyticsAPIView.as_view()),
]