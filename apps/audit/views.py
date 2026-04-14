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


from django.db import transaction
from django.shortcuts import get_object_or_404


class AuditMixin:
    """
    DRF View / ViewSet uchun universal audit mixin.

    Features:
    - action-based exclude (list, retrieve)
    - safe serialization (fallback bor)
    - transaction.on_commit bilan write
    - application resolve (instance / request / URL)
    - DRY create/update/delete override
    """

    audit_exclude_actions = ["list", "retrieve"]

    # ===================== CREATE =====================

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

    # ===================== UPDATE =====================

    def update(self, request, *args, **kwargs):
        return self._update(request, partial=False, *args, **kwargs)

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

    # ===================== DELETE =====================

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

    # ===================== LOGIC =====================

    def _log(self, request, instance, action, old_data, new_data):
        """
        Core audit writer (action-based filtering)
        """
        # 🔥 faqat list/retrieve skip
        if hasattr(self, "action") and self.action in self.audit_exclude_actions:
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

        # 🔥 transaction safe
        try:
            transaction.on_commit(_write)
        except Exception:
            # fallback (agar transaction yo‘q bo‘lsa)
            _write()

    # ===================== APPLICATION RESOLVE =====================

    def _resolve_application(self, instance, request):
        """
        Application ni aniqlash:
        1. instance o‘zi Application bo‘lsa
        2. instance.application mavjud bo‘lsa
        3. request.data ichida bo‘lsa
        4. URL params (nested route)
        """

        try:
            from apps.applications.models import Application
        except Exception:
            return None

        # 1. instance o‘zi application
        if isinstance(instance, Application):
            return instance

        # 2. FK orqali
        app = getattr(instance, "application", None)
        if app:
            return app

        # 3. request.data orqali
        application_id = request.data.get("application")
        if application_id:
            return self._safe_get_application(application_id)

        # 4. URL params (MUHIM FIX)
        application_id = (
            self.kwargs.get("application_pk")
            or self.kwargs.get("application_id")
            or self.kwargs.get("pk")
        )

        if application_id:
            return self._safe_get_application(application_id)

        return None

    def _safe_get_application(self, pk):
        try:
            from apps.applications.models import Application
            return Application.objects.get(pk=pk)
        except Exception:
            return None

    # ===================== SERIALIZATION =====================

    def _serialize(self, instance):
        """
        Safe serializer (fallback bor)
        """
        try:
            serializer_class = self.get_response_serializer()
            return serializer_class(instance).data
        except Exception:
            # fallback minimal data
            return {
                "id": getattr(instance, "pk", None),
                "repr": str(instance),
            }

    def _build_response(self, instance, status_code):
        from rest_framework.response import Response

        serializer_class = self.get_response_serializer()
        return Response(serializer_class(instance).data, status=status_code)

    def get_response_serializer(self):
        """
        Agar alohida response serializer bo‘lsa ishlatadi
        """
        return getattr(self, "response_serializer_class", self.get_serializer_class())
    

class AuditLogAPIView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, AuditPermissions]

    def get(self, request: Request, pk: int) -> Response:
        application = get_object_or_404(Application, pk=pk)

        logs = AuditLog.objects.filter(application = application).all()

        return Response(
            AuditlogsSerializers(logs, many=True).data
        )
