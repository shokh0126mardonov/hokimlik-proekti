from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.audit.views import AuditMixin
from .models import User
from .permissions import Is_SuperAdmin
from .serializers import UserSerializer, RegisterSerializers
from ..references.models import Mahalla

from django.db import IntegrityError


class UserCrudVievSet(AuditMixin, ModelViewSet):
    authentication_classes = [JWTAuthentication]
    queryset = User.objects.filter(is_active=True).all()
    permission_classes = [IsAuthenticated, Is_SuperAdmin]

    def get_serializer_class(self):
        if self.action in ["create", "partial_update"]:
            return RegisterSerializers
        elif self.action == "list":
            return UserSerializer
        else:
            return UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        role = serializer.validated_data.get("role")

        try:
            with transaction.atomic():
                user = serializer.save()

                # 🔐 Password hash (critical safety)
                if "password" in serializer.validated_data:
                    user.set_password(serializer.validated_data["password"])
                    user.save(update_fields=["password"])

        except IntegrityError as e:
            if hasattr(e.__cause__, "diag"):
                constraint = e.__cause__.diag.constraint_name

                if constraint == "unique_super_admin_hokim":
                    if role == "super_admin":
                        return Response(
                            {"role": ["Super admin already exists"]},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    elif role == "hokim":
                        return Response(
                            {"role": ["Hokim already exists"]},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

            return Response(
                {"detail": "Database constraint error"},
                status=status.HTTP_400_BAD_REQUEST,
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

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "role": user.role,
                "id": user.id,
                "service": getattr(user.service, "id", None),
            }
        )
    

import json
import secrets
import string
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from django.db import transaction
from .models import User


def generate_password(length=12):
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


class ImportOqsoqolView(APIView):
    permission_classes = [Is_SuperAdmin]
    parser_classes = [MultiPartParser, JSONParser]

    def post(self, request):
        if "file" in request.FILES:
            try:
                items = json.load(request.FILES["file"])
            except json.JSONDecodeError as e:
                return Response(
                    {"error": f"Noto'g'ri JSON: {e}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            items = request.data

        # 2) Bitta obyekt kelsa ham, listga o'rab olamiz
        if isinstance(items, dict):
            items = [items]

        if not isinstance(items, list):
            return Response(
                {"error": "JSON obyekt yoki ro'yxat (array) bo'lishi kerak"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created, skipped, errors = 0, 0, []
        created_users = []

        # 3) Har bir elementni qayta ishlash
        for i, item in enumerate(items):
            try:
                username = item.get("username")
                password = item.get("password")
                full_name = item.get("full_name")
                phone = item.get("phone")
                mahalla_name = item.get("mahalla")

                # Majburiy maydonlarni tekshirish
                if not all([username, full_name, phone, mahalla_name]):
                    errors.append(
                        f"#{i}: username, full_name, phone, mahalla majburiy"
                    )
                    continue

                # Telefon yoki username band bo'lsa — o'tkazib yuboramiz
                if User.objects.filter(phone=phone).exists():
                    skipped += 1
                    errors.append(f"#{i}: phone {phone} allaqachon mavjud")
                    continue

                if User.objects.filter(username=username).exists():
                    skipped += 1
                    errors.append(f"#{i}: username '{username}' allaqachon mavjud")
                    continue

                # 4) Mahallani topish yoki yaratish
                mahalla, _ = Mahalla.objects.get_or_create(
                    name=mahalla_name.strip(),
                )

                # 5) Foydalanuvchini yaratish
                with transaction.atomic():
                    user = User(
                        username=username,
                        full_name=full_name,
                        phone=phone,
                        role=User.Role.OQSOQOL,
                        mahalla=mahalla,
                        telegram_id=item.get("telegram_id"),
                        is_active=item.get("is_active", True),
                    )
                    final_password = password or generate_password()
                    user.set_password(final_password)
                    user.save()

                    created += 1
                    created_users.append({
                        "username": username,
                        "phone": str(phone),
                        "mahalla": mahalla.name,
                        "password": final_password,
                    })
            except Exception as e:
                errors.append(f"#{i}: {e}")

        return Response(
            {
                "created": created,
                "skipped": skipped,
                "errors": errors,
                "created_users": created_users,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
