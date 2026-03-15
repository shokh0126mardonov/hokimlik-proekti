from django.urls import path

from .views import ApplicationViewSets,AplicationsSendMahalla

urlpatterns = [
    path("applications/",ApplicationViewSets.as_view({"get":"list","post":"create"})),
    path("applications/<int:pk>/",ApplicationViewSets.as_view({"get":"retrieve","patch":"partial_update"})),

    path("applications/<int:pk>/send-to-mahalla/",AplicationsSendMahalla.as_view({"post":"create"}))

]
