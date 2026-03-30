import asyncio
from django.utils import timezone
from django.shortcuts import get_object_or_404

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.generics import ListCreateAPIView
from rest_framework import status

from apps.accounts.models import User
from apps.audit.views import AuditMixin
from .models import Application,Attachment,MahallaReport
from .serializers import AplicationSerializers,AttachmentSerializers,AttachmentResponseSerializers,MahallaRepostSerializers,AplicationUpdateSerializers
from .permission import AplicationPermission,AplicationCreatePermission,AplicationsSendMahallaPermissions,AttachmentPermissions
from .pagination import CustomPagination
from handlers.service.ogohlantirish import bot_send_message

class ApplicationViewSets(AuditMixin,ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = AplicationSerializers
    authentication_classes = [JWTAuthentication]
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action in ["list",'retrieve']:
            permission_classes = [IsAuthenticated,AplicationPermission]
        elif self.action in['create','partial_update']:
            permission_classes = [IsAuthenticated,AplicationCreatePermission]

        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == "partial_update":
            return AplicationUpdateSerializers
        



    def list(self, request, *args, **kwargs):

        if request.user.role in [User.Role.SUPER_ADMIN, User.Role.HOKIM]:
            queryset = Application.objects.all()

        elif request.user.role == User.Role.OQSOQOL:
            queryset = Application.objects.filter(mahalla=request.user.mahalla)

        elif request.user.role == User.Role.SERVICE_STAFF:
            queryset = Application.objects.filter(service=request.user.service)

        else:
            queryset = Application.objects.none()

        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):

        ariza = self.get_object()

        if request.user.role == User.Role.OQSOQOL:
            if ariza.mahalla ==  request.user.mahalla:
                serializer = self.get_serializer(ariza)
                return Response(serializer.data)
            return Response({"status":"Bu sizning mahallangizga biriktirilmagan"},status=400)
        
        elif request.user.role == User.Role.SERVICE_STAFF:
            if ariza.service == request.user.service:
                serializer = self.get_serializer(ariza)
                return Response(serializer.data)
            
            return Response({"status":"Bu sizning servisingizga biriktirilmagan"},status=400)
        
        elif request.user.role == User.Role.HOKIM:
            serializer = self.get_serializer(ariza)
            ariza.status = Application.Status.IN_REVIEW
            ariza.save(update_fields=['status'])
            

        return Response(self.get_serializer(ariza).data)

    def partial_update(self, request, *args, **kwargs):
        application = self.get_object()

        if application.status != Application.Status.NEW:
            return Response({"status": "permission denied"}, status=403)

        serializer = self.get_serializer(
            application,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)


    
    def perform_create(self, serializer):
        return serializer.save(created_by = self.request.user)


class SendToMahallaAPIView(AuditMixin,APIView):
    permission_classes = [IsAuthenticated, AplicationsSendMahallaPermissions]

    def post(self, request, pk):
        application = get_object_or_404(Application, pk=pk)

        application.sent_to_mahalla_at = timezone.now()
        application.status = 'sent_to_mahalla'

        mahalla = application.mahalla
        users = User.objects.filter(
            mahalla=mahalla,
            role=User.Role.OQSOQOL
        ).all()

        for user in users:
            telegram_id = user.telegram_id
            print(telegram_id)
            if telegram_id:
                asyncio.run(bot_send_message(chat_id=telegram_id,status=Application.Status.SENT_TO_MAHALLA))

        application.save(update_fields=['status','sent_to_mahalla_at'])
        return Response({'status': 'ok'})
    

class AplicationStatus(AuditMixin,ModelViewSet):
    queryset = Application.objects.all()
    permission_classes = [IsAuthenticated,AplicationsSendMahallaPermissions]
    authentication_classes = [JWTAuthentication]

    @action(detail=True,methods=['post'],url_path='archive')
    def archive(self,request:Request,pk):
        aplication = Application.objects.get(pk = pk)
        aplication.status = "archived"

        aplication.save(
            update_fields = ['status']
        )

        return Response({"status":"ok"})
    
    @action(detail=True,methods=['post'],url_path='close')
    def close(self,request:Request,pk):
        aplication = Application.objects.get(pk = pk)
        aplication.status = "closed"
        aplication.closed_at = timezone.now()
        aplication.save(
            update_fields = ['status','closed_at']
        )

        return Response({"status":"ok"})

    @action(detail=True,methods=['post'],url_path='reopen')
    def reopen(self,request:Request,pk):
        aplication = Application.objects.get(pk = pk)
        aplication.status = aplication.Status.REOPENED

        users = User.objects.filter(
            mahalla=aplication.mahalla,
            role=User.Role.OQSOQOL
        ).all()
        
        for user in users:
            telegram_id = user.telegram_id
            if telegram_id:
                asyncio.run(bot_send_message(chat_id=telegram_id,status=Application.Status.REOPENED))

        aplication.save(
            update_fields = ['status']
        )

        return Response({"status":"ok"})
    


class AttachmentApiView(AuditMixin,ListCreateAPIView):
    queryset = Attachment.objects.all()
    permission_classes = [IsAuthenticated,AttachmentPermissions]
    authentication_classes = [JWTAuthentication]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AttachmentSerializers
        return AttachmentResponseSerializers
    
    def create(self, request, *args, **kwargs):

        from ipware import get_client_ip
        client_ip, is_routable = get_client_ip(request)

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        instance = serializer.instance

        response_serializer = AttachmentResponseSerializers(instance)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_create(self, serializer):
        return serializer.save(
            uploaded_by = self.request.user
        )
            

class ExportFileViewSets(AuditMixin,ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated,AplicationsSendMahallaPermissions]
    queryset = Attachment.objects.all()
    serializer_class = AttachmentResponseSerializers


class MahallaRepost(AuditMixin,ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated,AplicationsSendMahallaPermissions]
    queryset = MahallaReport.objects.all()
    serializer_class = MahallaRepostSerializers




# apps/dashboard/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .services import get_dashboard_summary


class DashboardSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        data = get_dashboard_summary()
        return Response(data)
    
class OqsoqolActivityAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated,AplicationsSendMahallaPermissions]
    serializer_class = AttachmentResponseSerializers

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk,role = User.Role.OQSOQOL)

        acknowledged = Application.objects.filter(mahalla=user.mahalla,status=Application.Status.ACKNOWLEDGED).count()
        inspected = Application.objects.filter(mahalla=user.mahalla,status=Application.Status.INSPECTED).count()
        closed = Application.objects.filter(mahalla=user.mahalla,status=Application.Status.CLOSED).count()
        reopened = Application.objects.filter(mahalla=user.mahalla,status=Application.Status.REOPENED).count()

        return Response({
            "oqsoqol ko'rgan arizalar":acknowledged,
            "oqsoqol tekshirgan arizalar":inspected,
            "yopilgan arizalar":closed,
            "qayta ochilgan arizalar":reopened
        })