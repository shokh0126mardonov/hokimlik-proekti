from django.urls import path
from .views import AnalyticsAPIView


from django.urls import path
from .views import *

urlpatterns = [
    path("analytics/insights/", AIInsightsAPIView.as_view()),
    path("analytics/service/<int:service_id>/", ServiceDetailAPIView.as_view()),
    path("analytics/mahalla/", MahallaAnalyticsAPIView.as_view()),
    path("analytics/sla-breakers/", SLABreakersAPIView.as_view()),
    path("analytics/oqsoqol/<int:oqsoqol_id>/", AnalyticsAPIView.as_view()),

]