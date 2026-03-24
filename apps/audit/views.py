from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from apps.applications.models import Application
from .models import AuditLog
from .serializers import AuditlogsSerializers
from .permissions import AuditPermissions
# apps/audit/mixins.py



class AuditMixin:
    audit_exclude_methods = ["GET", "HEAD", "OPTIONS"]

    # ===== CREATE =====
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        instance = serializer.instance
        new_data = self._serialize(instance)

        self._log(
            request=request,
            instance=instance,
            action="CREATE",
            old_data=None,
            new_data=new_data,
        )

        return self._build_response(instance, 201)

    # ===== UPDATE =====
    def update(self, request, *args, **kwargs):
        return self._update(request, partial=False, *args, **kwargs)

    # ===== PATCH =====
    def partial_update(self, request, *args, **kwargs):
        return self._update(request, partial=True, *args, **kwargs)

    def _update(self, request, partial, *args, **kwargs):
        instance = self.get_object()
        old_data = self._serialize(instance)

        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)

        updated_instance = serializer.instance
        new_data = self._serialize(updated_instance)

        self._log(
            request=request,
            instance=updated_instance,
            action="PATCH" if partial else "UPDATE",
            old_data=old_data,
            new_data=new_data,
        )

        return self._build_response(updated_instance, 200)

    # ===== DELETE =====
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        old_data = self._serialize(instance)

        self.perform_destroy(instance)

        self._log(
            request=request,
            instance=instance,
            action="DELETE",
            old_data=old_data,
            new_data=None,
        )

        from rest_framework.response import Response
        return Response(status=204)

    # ===== CORE LOGIC =====

    def _log(self, request, instance, action, old_data, new_data):
        if request.method in self.audit_exclude_methods:
            return

        from apps.audit.models import AuditLog
        from ipware import get_client_ip

        client_ip, _ = get_client_ip(request)

        application = self._resolve_application(instance, request)

        def _write():
            AuditLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                entity_type=instance.__class__.__name__,
                entity_id=str(instance.pk),
                action=action,
                old_data=old_data,
                new_data=new_data,
                ip_address=client_ip,
                application=application,
            )

        transaction.on_commit(_write)


    def _resolve_application(self, instance, request):
        from apps.applications.models import Application

        if isinstance(instance, Application):
            return instance

        # 1. instance.application
        app = getattr(instance, "application", None)
        if app:
            return app

        # 2. request.data
        application_id = request.data.get("application")
        if application_id:
            return self._get_application(application_id)

        # 3. URL (nested routes)
        application_id = (
            self.kwargs.get("application_pk")
            or self.kwargs.get("application_id")
        )
        if application_id:
            return self._get_application(application_id)

        return None

    def _get_application(self, pk):
        from applications.models import Application

        try:
            return Application.objects.get(pk=pk)
        except Application.DoesNotExist:
            return None

    # ===== SERIALIZATION =====

    def _serialize(self, instance):
        serializer_class = self.get_response_serializer()
        return serializer_class(instance).data

    def _build_response(self, instance, status_code):
        from rest_framework.response import Response

        serializer_class = self.get_response_serializer()
        return Response(serializer_class(instance).data, status=status_code)

    def get_response_serializer(self):
        return self.get_serializer_class()
    

class AuditLogAPIView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, AuditPermissions]

    def get(self, request: Request, pk: int) -> Response:
        application = get_object_or_404(Application, pk=pk)

        logs = application.audit_logs.all()

        return Response(
            AuditlogsSerializers(logs, many=True).data
        )
