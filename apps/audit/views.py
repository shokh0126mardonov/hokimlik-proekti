from django.db import transaction
from ipware import get_client_ip


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

        return self._build_response(instance, status_code=201)

    # ===== UPDATE =====
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
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
            action="UPDATE" if not partial else "PARTIAL_UPDATE",
            old_data=old_data,
            new_data=new_data,
        )

        return self._build_response(updated_instance, status_code=200)

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

    # ===== INTERNAL HELPERS =====

    def _log(self, request, instance, action, old_data, new_data):
        if request.method in self.audit_exclude_methods:
            return

        from apps.audit.models import AuditLog

        client_ip, _ = get_client_ip(request)

        def _write():
            AuditLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                entity_type=instance.__class__.__name__,
                entity_id=str(instance.pk),
                action=action,
                old_data=old_data,
                new_data=new_data,
                ip_address=client_ip,
            )

        # 🔥 transaction safe
        transaction.on_commit(_write)

    def _serialize(self, instance):
        serializer_class = self.get_response_serializer()
        return serializer_class(instance).data

    def _build_response(self, instance, status_code):
        from rest_framework.response import Response

        serializer_class = self.get_response_serializer()
        return Response(serializer_class(instance).data, status=status_code)

    # ===== OVERRIDABLE HOOK =====

    def get_response_serializer(self):
        """
        Agar alohida response serializer bo‘lsa override qilasan
        """
        return self.get_serializer_class()