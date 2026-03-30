import pandas as pd

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




class ExcelUploadView(APIView):
    
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated,Is_SuperAdmin]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        file = request.FILES.get("file")

        if not file:
            return Response({"error": "File yuborilmadi"}, status=400)

        df = pd.read_excel(file)

        # columnlarni rename qilish
        df.columns = ["id", "mahalla", "full_name", "phone"]

        # cleaning
        df = df[~df["mahalla"].astype(str).str.contains("sektor", case=False, na=False)]
        df = df.dropna(subset=["mahalla", "full_name", "phone"])

        df["phone"] = df["phone"].astype(str).str.replace(r"\D", "", regex=True)

        # output
        result = []
        for row in df.itertuples(index=False):
            item = {
                "mahalla": row.mahalla,
                "full_name": row.full_name,
                "phone": row.phone,
            }
            print(item)
            result.append(item)

        return Response({"data": result})