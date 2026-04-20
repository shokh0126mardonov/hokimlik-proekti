# apps/applications/services.py

import os
from django.conf import settings
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image as RLImage,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4


BASE_URL = "http://127.0.0.1:8000"  # prod’da domain qo‘yasan


def generate_application_pdf(application, report, attachments, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()

    # 🔹 Styles
    center_style = ParagraphStyle(
        name="Center",
        parent=styles["Normal"],
        alignment=1,
        fontSize=12,
        spaceAfter=5
    )

    title_style = ParagraphStyle(
        name="Title",
        parent=styles["Title"],
        alignment=1,
        spaceAfter=20
    )

    elements = []

    # ================= HEADER =================
    elements.append(Paragraph("SAMARQAND VILOYATI", center_style))
    elements.append(Paragraph("NARPAY TUMANI", center_style))
    elements.append(
        Paragraph(
            f"{application.mahalla.name if application.mahalla else ''} MAHALLASI",
            center_style
        )
    )

    elements.append(Spacer(1, 20))
    elements.append(Paragraph("<b>ARIZA HISOBOTI</b>", title_style))

    # ================= TABLE =================
    table_data = [
        ["Ariza ID", application.id],
        ["Fuqaro", application.citizen_name],
        ["Telefon", application.citizen_phone or "-"],
        ["Manzil", application.address_text],
        ["Sana", str(application.created_at.date())],
    ]

    table = Table(table_data, colWidths=[130, 330])
    table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    # ================= ARIZA =================
    elements.append(Paragraph("<b>Ariza matni:</b>", styles["Heading2"]))
    elements.append(Paragraph(application.content, styles["Normal"]))
    elements.append(Spacer(1, 20))

    # ================= REPORT =================
    oqsoqol_name = (
        report.oqsoqol.username
        if report and report.oqsoqol else "-"
    )

    comment = report.comment_text if report else "Izoh yo‘q"

    elements.append(Paragraph("<b>Mahalla hisobot:</b>", styles["Heading2"]))
    elements.append(Paragraph(f"Oqsoqol: <b>{oqsoqol_name}</b>", styles["Normal"]))
    elements.append(
        Paragraph(
            f"Sana: {report.created_at.date() if report else '-'}",
            styles["Normal"]
        )
    )
    elements.append(Spacer(1, 10))

    # 🔹 Izoh box
    comment_table = Table([[comment]], colWidths=[460])
    comment_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("PADDING", (0, 0), (-1, -1), 10),
    ]))

    elements.append(comment_table)
    elements.append(Spacer(1, 20))

    # ================= ATTACHMENTS =================
    elements.append(Paragraph("<b>Biriktirilgan fayllar:</b>", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    if not attachments:
        elements.append(Paragraph("Fayl mavjud emas", styles["Normal"]))

    for att in attachments:
        try:
            path = att.file.path

            # 📷 IMAGE → PDF ichida ko‘rinadi
            if path.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                img = RLImage(path)
                img.drawHeight = 250
                img.drawWidth = 350
                elements.append(img)
                elements.append(Spacer(1, 15))

            # 📎 FILE → clickable download link
            else:
                download_url = f"{BASE_URL}/api/v1/attachments/{att.id}/download/"

                elements.append(
                    Paragraph(
                        f'<a href="{download_url}">📎 Faylni yuklab olish</a>',
                        styles["Normal"]
                    )
                )
                elements.append(Spacer(1, 10))

        except Exception:
            elements.append(Paragraph("Fayl yuklanmadi", styles["Normal"]))

    # ================= FOOTER =================
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("__________________________", styles["Normal"]))
    elements.append(Paragraph("Oqsoqol imzosi", styles["Normal"]))

    doc.build(elements)