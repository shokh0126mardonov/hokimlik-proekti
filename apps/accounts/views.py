
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import CreateAPIView

from apps.audit.views import AuditMixin
from .models import User
from .permissions import Is_SuperAdmin
from .serializers import UserSerializer,RegisterSerializers,OqsoqolAddSerializers

from django.db import IntegrityError

class UserCrudVievSet(AuditMixin,ModelViewSet):

    authentication_classes = [JWTAuthentication]
    queryset = User.objects.filter(is_active = True).all()
    permission_classes = [IsAuthenticated,Is_SuperAdmin]

    def get_serializer_class(self):
        if self.action in ['create',"partial_update"]:
            return RegisterSerializers
        elif self.action == "list":
            return UserSerializer
        else:
            return UserSerializer
        
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            self.perform_create(serializer)

        except IntegrityError as e:
            # PostgreSQL constraint name ni to‘g‘ri olish
            if hasattr(e.__cause__, "diag"):
                constraint = e.__cause__.diag.constraint_name
                if constraint == "unique_super_admin":
                    return Response(
                        {"role": ["Super admin already exists"]},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            return Response(
                {"detail": "Database constraint error"},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = serializer.data
        data.pop("password", None)

        return Response(data, status=status.HTTP_201_CREATED)
    
    def perform_update(self, serializer):
        instance = self.get_object()

        old_phone = instance.phone
        new_phone = serializer.validated_data.get("phone", old_phone)

        password = serializer.validated_data.get("password", None)

        if old_phone != new_phone:
            user = serializer.save(telegram_id=None)
        else:
            user = serializer.save()

        if password:
            user.set_password(password)
            user.save(update_fields=["password"])

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


class LoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.user

        if not user.is_active:
            return Response({"detail": "User is not active"}, status=401)

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'role': user.role,
            'id': user.id,
            "service": getattr(user.service, "id", None)  
        })


from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
import json

class AddOqsoqol(AuditMixin, CreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, Is_SuperAdmin]
    serializer_class = OqsoqolAddSerializers

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = serializer.validated_data['file']

        # if not file.name.lower().endswith('.json'):
        #     return Response("json file yuboring",400)

        
        

        return Response({"detail": "Oqsoqollar muvaffaqiyatli qo‘shildi"}, status=201)