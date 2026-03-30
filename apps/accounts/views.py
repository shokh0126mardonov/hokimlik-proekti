
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from uritemplate import api

from apps.references.models import Mahalla
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
   
    def perform_update(self, serializer):
        instance = self.get_object()

        old_phone = instance.phone
        new_instance = serializer.save()

        if old_phone != new_instance.phone:
            new_instance.telegram_id = None
            new_instance.save(update_fields=["telegram_id"])

class LoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except AuthenticationFailed as e:
            return Response({"detail": str(e)}, status=401)

        user = serializer.user
        if not user.is_active:
            return Response({"detail": "User is not active"}, status=401)

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'role': user.role
        })



