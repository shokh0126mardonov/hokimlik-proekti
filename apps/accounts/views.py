from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.audit.views import AuditMixin
from .models import User
from .permissions import Is_SuperAdmin
from .serializers import UserSerializer,RegisterSerializers


class UserCrudVievSet(AuditMixin,ModelViewSet):
    authentication_classes = [JWTAuthentication]
    queryset = User.objects.filter(is_active = True).all()
    permission_classes = [IsAuthenticated,Is_SuperAdmin]

    def get_serializer_class(self):
        if self.action in ['create',"partial_update"]:
            return RegisterSerializers
        elif self.action == "list":
            return UserSerializer
        
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        data = serializer.data
        data.pop("password")
        return Response(data,status=201)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save(update_fields=["is_active"])

        return Response(status=204)