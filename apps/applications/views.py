import asyncio
from django.utils import timezone
from django.db.models import Q
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
from .models import Application, Attachment, MahallaReport
from .serializers import (
    AplicationSerializers,
    AttachmentSerializers,
    AttachmentResponseSerializers,
    MahallaRepostSerializers,
    AplicationUpdateSerializers,
)
from .permission import (
    AplicationPermission,
    AplicationCreatePermission,
    AplicationsSendMahallaPermissions,
    AttachmentPermissions,
    AttachmentGetPermissions,
)
from .pagination import CustomPagination
from handlers.service.ogohlantirish import bot_send_message
from .services import get_dashboard_summary
from .ai import generate_application_pdf


class ApplicationViewSets(AuditMixin, ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = AplicationSerializers
    authentication_classes = [JWTAuthentication]
    pagination_class = CustomPagination

    @action(detail=True, methods=["get"], url_path="attachments-to-pdf")
    def attachments_to_pdf(self, request, pk=None):
        application = self.get_object()

        report = application.reports.first()

        attachments = Attachment.objects.filter(
            Q(application=application) | Q(report=report)
        )

        pdf_path = os.path.join(
            settings.MEDIA_ROOT, "pdfs", f"app_{application.id}.pdf"
        )

        generate_application_pdf(
            application=application,
            report=report,
            attachments=attachments,
            output_path=pdf_path,
        )

        return FileResponse(
            open(pdf_path, "rb"),
            content_type="application/pdf",
            as_attachment=True,
            filename=f"application_{application.id}.pdf",
        )

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsAuthenticated, AplicationPermission]
        elif self.action in ["create", "partial_update"]:
            permission_classes = [IsAuthenticated, AplicationCreatePermission]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == "partial_update":
            return AplicationUpdateSerializers
        else:
            return AplicationSerializers

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
            if ariza.mahalla == request.user.mahalla:
                serializer = self.get_serializer(ariza)
                return Response(serializer.data)
            return Response(
                {"status": "Bu sizning mahallangizga biriktirilmagan"}, status=400
            )

        elif request.user.role == User.Role.SERVICE_STAFF:
            if ariza.service == request.user.service:
                serializer = self.get_serializer(ariza)
                return Response(serializer.data)

            return Response(
                {"status": "Bu sizning servisingizga biriktirilmagan"}, status=400
            )

        elif request.user.role == User.Role.HOKIM:
            serializer = self.get_serializer(ariza)
            if ariza.status == Application.Status.NEW:
                ariza.status = Application.Status.IN_REVIEW
                ariza.save(update_fields=["status"])

        return Response(self.get_serializer(ariza).data)

    def partial_update(self, request, *args, **kwargs):
        application = self.get_object()

        if application.status != Application.Status.NEW:
            return Response({"status": "permission denied"}, status=403)

        return super().partial_update(request, *args, **kwargs)

        serializer = self.get_serializer(application, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_create(self, serializer):
        return serializer.save(created_by=self.request.user)


class SendToMahallaAPIView(AuditMixin, APIView):
    permission_classes = [IsAuthenticated, AplicationsSendMahallaPermissions]

    def post(self, request, pk):
        application = get_object_or_404(Application, pk=pk)

        application.sent_to_mahalla_at = timezone.now()
        application.status = "sent_to_mahalla"

        mahalla = application.mahalla
        users = User.objects.filter(mahalla=mahalla, role=User.Role.OQSOQOL).all()

        for user in users:
            telegram_id = user.telegram_id
            print(telegram_id)
            if telegram_id:
                asyncio.run(
                    bot_send_message(
                        chat_id=telegram_id, status=Application.Status.SENT_TO_MAHALLA
                    )
                )

        application.save(update_fields=["status", "sent_to_mahalla_at"])
        return Response({"status": "ok"})


class AplicationStatus(AuditMixin, ModelViewSet):
    queryset = Application.objects.all()
    permission_classes = [IsAuthenticated, AplicationsSendMahallaPermissions]
    authentication_classes = [JWTAuthentication]

    @action(detail=True, methods=["post"], url_path="archive")
    def archive(self, request: Request, pk):
        aplication = Application.objects.get(pk=pk)
        aplication.status = "archived"

        aplication.save(update_fields=["status"])

        return Response({"status": "ok"})

    @action(detail=True, methods=["post"], url_path="close")
    def close(self, request: Request, pk):
        aplication = Application.objects.get(pk=pk)
        aplication.status = "closed"
        aplication.closed_at = timezone.now()
        aplication.save(update_fields=["status", "closed_at"])

        return Response({"status": "ok"})

    @action(detail=True, methods=["post"], url_path="reopen")
    def reopen(self, request: Request, pk):
        aplication = Application.objects.get(pk=pk)
        aplication.status = aplication.Status.REOPENED

        users = User.objects.filter(
            mahalla=aplication.mahalla, role=User.Role.OQSOQOL
        ).all()

        for user in users:
            telegram_id = user.telegram_id
            if telegram_id:
                asyncio.run(
                    bot_send_message(
                        chat_id=telegram_id, status=Application.Status.REOPENED
                    )
                )

        aplication.save(update_fields=["status"])

        return Response({"status": "ok"})


class AttachmentApiView(AuditMixin, ListCreateAPIView):
    queryset = Attachment.objects.all()
    permission_classes = [IsAuthenticated, AttachmentPermissions]
    authentication_classes = [JWTAuthentication]
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.request.method == "GET":
            permission_classes = [IsAuthenticated, AttachmentGetPermissions]
        else:
            permission_classes = [IsAuthenticated, AttachmentPermissions]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AttachmentSerializers
        return AttachmentResponseSerializers

    def list(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        aplication = get_object_or_404(Application, pk=pk)

        data = Attachment.objects.filter(application=aplication).all()
        return Response(AttachmentResponseSerializers(data, many=True).data)

    def create(self, request, *args, **kwargs):
        application_id = self.kwargs.get("pk")

        application = get_object_or_404(Application, id=application_id)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = serializer.save(application=application)

        response_serializer = AttachmentResponseSerializers(instance)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        return serializer.save(uploaded_by=self.request.user)


class ExportFileViewSets(AuditMixin, ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, AplicationsSendMahallaPermissions]
    queryset = Attachment.objects.all()
    serializer_class = AttachmentResponseSerializers


class MahallaRepost(AuditMixin, ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, AplicationsSendMahallaPermissions]
    queryset = MahallaReport.objects.all()
    serializer_class = MahallaRepostSerializers


class DashboardSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = get_dashboard_summary()
        return Response(data)


class OqsoqolActivityAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, AplicationsSendMahallaPermissions]

    def get(self, request, pk):
        user = User.objects.filter(pk=pk, role=User.Role.OQSOQOL).first()

        if not user:
            return Response({"detail": "User not found"}, status=404)

        mahalla = user.mahalla

        if not mahalla:
            return Response("mahallaga biriktirilmagan", 400)

        qs = Application.objects.filter(mahalla=mahalla)

        return Response(
            {
                "oqsoqol ko'rgan arizalar": qs.filter(
                    status=Application.Status.ACKNOWLEDGED
                ).count(),
                "oqsoqol tekshirgan arizalar": qs.filter(
                    status=Application.Status.INSPECTED
                ).count(),
                "yopilgan arizalar": qs.filter(
                    status=Application.Status.CLOSED
                ).count(),
                "qayta ochilgan arizalar": qs.filter(
                    status=Application.Status.REOPENED
                ).count(),
            }
        )


import os
from django.http import FileResponse, Http404
from django.conf import settings
from rest_framework.views import APIView


class DownloadAttachmentAPIView(APIView):
    def get(self, request, pk):
        from .models import Attachment

        try:
            attachment = Attachment.objects.get(pk=pk)
        except Attachment.DoesNotExist:
            raise Http404("File not found")

        file_path = attachment.file.path

        if not os.path.exists(file_path):
            raise Http404("File not found on disk")

        return FileResponse(
            open(file_path, "rb"),
            as_attachment=True,
            filename=os.path.basename(file_path),
        )
