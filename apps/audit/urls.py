from django.urls import path

from .views import AuditLogAPIView

urlpatterns = [
    path("applications/<int:pk>/timeline/", AuditLogAPIView.as_view()),
]
