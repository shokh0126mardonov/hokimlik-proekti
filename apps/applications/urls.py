from django.urls import path

from .views import ApplicationViewSets,SendToMahallaAPIView,AplicationStatus,AttachmentApiView

urlpatterns = [
    path("applications/",ApplicationViewSets.as_view({"get":"list","post":"create"})),
    path("applications/<int:pk>/",ApplicationViewSets.as_view({"get":"retrieve","patch":"partial_update"})),

    path("applications/<int:pk>/send-to-mahalla/",SendToMahallaAPIView.as_view()),

    path("applications/<int:pk>/archive/",AplicationStatus.as_view({"post":"archive"})),
    path("applications/<int:pk>/close/",AplicationStatus.as_view({"post":"close"})),
    path("applications/<int:pk>/reopen/",AplicationStatus.as_view({"post":"reopen"})),

    #File yuklash
    path("applications/<int:pk>/attachments/",AttachmentApiView.as_view())

]
