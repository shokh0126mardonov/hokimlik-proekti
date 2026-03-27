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
from .serializers import AplicationSerializers,AttachmentSerializers,AttachmentResponseSerializers,MahallaRepostSerializers
from .permission import AplicationPermission,AplicationCreatePermission,AplicationsSendMahallaPermissions,AttachmentPermissions
from .pagination import CustomPagination

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

        return Response(self.get_serializer(ariza).data)

    def perform_create(self, serializer):
        return serializer.save(created_by = self.request.user)


class SendToMahallaAPIView(AuditMixin,APIView):
    permission_classes = [IsAuthenticated, AplicationsSendMahallaPermissions]

    def post(self, request, pk):
        application = Application.objects.get(pk=pk)

        if application.status != 'new':
            return Response({'error': 'Invalid state'})

        application.sent_to_mahalla_at = timezone.now()
        application.status = 'sent_to_mahalla'

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
        aplication.status = "reopened"

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