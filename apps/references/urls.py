from django.urls import path

from .views import MahallaViewsets

urlpatterns = [
    path("mahallas/",MahallaViewsets.as_view({"get":"list","post":"create",})),
    path("mahallas/<int:pk>/",MahallaViewsets.as_view({"get":"retrieve","patch":"partial_update","delete":"destroy","put":"update"})),

]
