from django.urls import path

from .views import MahallaViewsets, ServiceViewsets, ApplicationTypeViewsets

urlpatterns = [
    path(
        "mahallas/",
        MahallaViewsets.as_view(
            {
                "get": "list",
                "post": "create",
            }
        ),
    ),
    path(
        "mahallas/<int:pk>/",
        MahallaViewsets.as_view(
            {
                "get": "retrieve",
                "patch": "partial_update",
                "delete": "destroy",
                "put": "update",
            }
        ),
    ),
    path(
        "services/",
        ServiceViewsets.as_view(
            {
                "get": "list",
                "post": "create",
            }
        ),
    ),
    path(
        "services/<int:pk>/",
        ServiceViewsets.as_view(
            {
                "get": "retrieve",
                "patch": "partial_update",
                "delete": "destroy",
                "put": "update",
            }
        ),
    ),
    path(
        "application-types/",
        ApplicationTypeViewsets.as_view(
            {
                "get": "list",
                "post": "create",
            }
        ),
    ),
    path(
        "application-types/<int:pk>/",
        ApplicationTypeViewsets.as_view(
            {
                "get": "retrieve",
                "patch": "partial_update",
                "delete": "destroy",
                "put": "update",
            }
        ),
    ),
]
