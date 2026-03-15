from django.shortcuts import get_object_or_404

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Application
from .serializers import AplicationSerializers,SendMahallaSerialisers
from .permission import AplicationPermission,AplicationCreatePermission,AplicationsSendMahallaPermissions

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


    def perform_create(self, serializer):
        return serializer.save(created_by = self.request.user)
    

class AplicationsSendMahalla(ModelViewSet):

    queryset = Application.objects.all()
    authentication_classes = [JWTAuthentication]
    serializer_class = SendMahallaSerialisers

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAuthenticated,AplicationsSendMahallaPermissions]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        mahalla_id = request.data.get("id")
        aplication = get_object_or_404(Application,pk=id)


        