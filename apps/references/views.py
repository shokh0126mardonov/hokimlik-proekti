from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from apps.audit.views import AuditMixin
from .models import Mahalla
from .serializers import MahallaSerializers
from .permissions import GetMahallaPermissions

class MahallaViewsets(AuditMixin,ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Mahalla.objects.all()
    serializer_class = MahallaSerializers

    def get_permissions(self):
        if self.action in ["list","retrive"]:
            permission_classes  = [IsAuthenticated]
        else:
            permission_classes = [GetMahallaPermissions]

        return [permission() for permission in permission_classes]