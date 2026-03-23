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




from .models import Application
from .serializers import AplicationSerializers,AttachmentSerializers
from .permission import AplicationPermission,AplicationCreatePermission,AplicationsSendMahallaPermissions,AttachmentPermissions

class ApplicationViewSets(ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = AplicationSerializers
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action in ["list",'retrieve']:
            permission_classes = [IsAuthenticated,AplicationPermission]
        elif self.action in['create','partial_update']:
            permission_classes = [IsAuthenticated,AplicationCreatePermission]

        return [permission() for permission in permission_classes]


    def list(self, request, *args, **kwargs):

        if request.user.role in ['super_admin','hokim']:
            queryset = Application.objects.all()

        elif request.user.role == 'oqsoqol':
            queryset = Application.objects.filter(mahalla = request.user.mahalla).all()

        elif request.user.role == 'service_staff':  
            queryset = Application.objects.filter(service = request.user.service).all()

        serializers = self.get_serializer(queryset,many=True)
        return Response(serializers.data)
    
    def retrieve(self, request, *args, **kwargs):

        ariza = self.get_object()

        if request.user.role == 'oqsoqol':
            if ariza.mahalla ==  request.user.mahalla:
                serializer = self.get_serializer(ariza)
                return Response(serializer.data)
            return Response({"status":"Bu sizning mahallangizga biriktirilmagan"},status=400)
        
        elif request.user.role == 'service_staff':
            if ariza.service == request.user.service:
                serializer = self.get_serializer(ariza)
                return Response(serializer.data)
            return Response({"status":"Bu sizning servisingizga biriktirilmagan"},status=400)

        return Response(self.get_serializer(ariza).data)

    def perform_create(self, serializer):
        return serializer.save(created_by = self.request.user)


class SendToMahallaAPIView(APIView):
    permission_classes = [IsAuthenticated, AplicationsSendMahallaPermissions]

    def post(self, request, pk):
        application = Application.objects.get(pk=pk)

        if application.status != 'new':
            return Response({'error': 'Invalid state'})

        application.sent_to_mahalla_at = timezone.now()
        application.status = 'sent_to_mahalla'

        application.save(update_fields=['status','sent_to_mahalla_at'])
        return Response({'status': 'ok'})
    

class AplicationStatus(ModelViewSet):
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
    


class AttachmentApiView(APIView):
    permission_classes = [IsAuthenticated,AttachmentPermissions]
    authentication_classes = [JWTAuthentication]
    parser_classes = [MultiPartParser, FormParser]

    def post(self,request:Request,pk)->Response:
        aplication = get_object_or_404(Application,pk=pk)
        
        serializers = AttachmentSerializers(data = request.data)
        serializers.is_valid(raise_exception=True)

        serializers.save(
            application = aplication,
            uploaded_by = request.user
        )
        return Response({"status":"ok"})
    
    