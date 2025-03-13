from django.shortcuts import render, redirect
from django_tables2 import RequestConfig
from django.contrib import messages
from django.conf import settings
from django.utils.timezone import localtime
import django_tables2 as tables
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.auth.models import User
import csv
from .models import Order
from .filters import OrderFilter
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image as RLImage,
)
from django.http import HttpResponse
import os
from PIL import Image, ImageOps
import io
from datetime import datetime
import openpyxl


# from .tables import OrderTable


def generate_order_pdf(request, order_id):
    try:
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        return HttpResponse("Order not found", status=400)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="order_{order_id}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    title = Paragraph(
        f"<para fontSize=16><b>Order Details - #{order.order_id}</b></para>",
        styles["Title"],
    )
    elements.append(title)
    elements.append(Spacer(1, 20))

    sketch_image = ""
    cad_image = ""

    if order.sketch and os.path.exists(order.sketch.path):
        sketch_image = RLImage(order.sketch.path, width=200, height=150)

    if order.cad_file and order.cad_file.path and os.path.exists(order.cad_file.path):
        cad_path = order.cad_file.path
        processed_cad_img = cad_file_process(cad_path)

        if processed_cad_img:
            cad_image = RLImage(processed_cad_img, width=220, height=170)

    description = Paragraph(
        "CAD Image (with 10% whitespace margin,<br/>1000x1000px<br/>Guyal logo at top right corner)",
        styles["Normal"],
    )
    image_data = [
        [sketch_image, cad_image],
        [
            "Reference Image",
            description,
        ],
    ]
    image_table = Table(image_data, colWidths=(270, 270))
    elements.append(image_table)
    elements.append(Spacer(1, 20))

    order_details_cleaned = str(order.order_details or "")

    details_style = ParagraphStyle(name="DetailsStyle", leading=14)

    details_paragraph = Paragraph(
        order_details_cleaned.replace("\n", "<br/>"), details_style
    )

    data = [
        ["Name", "Value"],
        ["Jewellery Type:", order.jewellery_type],
        [
            "Order Date:",
            order.created_at.strftime("%Y-%m-%d") if order.created_at else "N/A",
        ],
        ["Order Details:", details_paragraph],
    ]

    if not request.user.groups.filter(name="Factory Manager").exists():
        data.insert(
            2,
            ["Customer", order.customer],
        )

    table = Table(data, colWidths=[280, 280])

    style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("WORDWRAP", (1, 1), (-1, -1), "CJK"),
        ]
    )

    table.setStyle(style)

    elements.append(table)

    doc.build(elements)
    return response


def order_table_view(request):
    user = request.user
    view_columns = []

    if user.groups.filter(name="Store Manager").exists() or user.is_superuser:
        view_columns = [
            "order_id",
            "jewellery_type",
            "order_details",
            "manufacturing_cost",
            "margin",
            "customer",
            "created_at",
            "img",
            "pdf",
        ]
    elif user.groups.filter(name="Factory Manager").exists():
        view_columns = [
            "order_id",
            "jewellery_type",
            "order_details",
            "manufacturing_cost",
            "created_at",
            "img",
            "pdf",
        ]
    elif user.groups.filter(name="Customer").exists():
        view_columns = [
            "order_id",
            "jewellery_type",
            "order_details",
            "created_at",
            "total_cost",
            "img",
            "pdf",
        ]

    order_filter = OrderFilter(request.GET, queryset=Order.objects.all())

    if user and not user.is_superuser:
        if user.groups.filter(name="Customer").exists():
            order_filter = OrderFilter(
                request.GET, queryset=Order.objects.filter(customer=request.user)
            )

    queryset = order_filter.qs
    for order in queryset:
        manufacturing_cost = (
            order.manufacturing_cost if order.manufacturing_cost is not None else 0
        )
        margin = order.margin if order.margin is not None else 0

        order.total_cost = manufacturing_cost + (manufacturing_cost * (margin / 100))

    class DynamicOrderTable(tables.Table):
        class Meta:
            model = Order
            template_name = "django_tables2/bootstrap4.html"
            fields = view_columns
            order_by = "created_at"

        if "total_cost" in view_columns:
            total_cost = tables.Column(empty_values=(), verbose_name="Total Cost")

            def render_total_cost(self, value, record):
                manufacturing_cost = record.manufacturing_cost or 0
                margin = record.margin or 0
                total_cost = manufacturing_cost + (manufacturing_cost * (margin / 100))

                formatted_total_cost = "{:.2f}".format(total_cost)
                return format_html(
                    '<p style="text-align: center; margin: 0;">{}</p>',
                    formatted_total_cost,
                )

        if "pdf" in view_columns:
            pdf = tables.Column(empty_values=(), verbose_name="PDF")

            def render_pdf(self, record):
                pdf_url = reverse(
                    "generate_order_pdf", kwargs={"order_id": record.order_id}
                )
                return format_html(
                    '<a href="{}" class="btn btn-primary btn-sm" target="_blank">Generate PDF</a>',
                    pdf_url,
                )

        if "img" in view_columns:
            img = tables.Column(empty_values=(), verbose_name="Image")

            def render_img(self, record):
                img_url = reverse("generate_cad", kwargs={"order_id": record.pk})
                return format_html(
                    '<a href="{}" class="btn btn-primary btn-sm" target="_blank">Generate CAD</a>',
                    img_url,
                )

    table = DynamicOrderTable(order_filter.qs)
    RequestConfig(request, paginate={"per_page": 10}).configure(table)

    return render(
        request,
        "admin/order_table.html",
        {
            "table": table,
            "filter": order_filter,
            "view_columns": view_columns,
        },
    )


# CAD File Process function without stretching out the cad image (Maintaining its aspect ratio)
# def cad_file_process(image_path, canvas_size=(1000, 1000)):

#     img = Image.open(image_path).convert("RGBA")
#     logo_path = os.path.join(settings.BASE_DIR, "static/images/guyal_logo.png")

#     img.thumbnail((canvas_size[0] - 20, canvas_size[1] - 20), Image.LANCZOS)  # 20px margin

#     canvas = Image.new("RGBA", canvas_size, "white")

#     paste_x = (canvas_size[0] - img.size[0]) // 2
#     paste_y = (canvas_size[1] - img.size[1]) // 2

#     canvas.paste(img, (paste_x, paste_y), img)

#     canvas = ImageOps.expand(canvas, border=5, fill="black")

#     if os.path.exists(logo_path):
#         logo = Image.open(logo_path).convert("RGBA")
#         logo_size = (int(canvas_size[0] * 0.1), int(canvas_size[1] * 0.1))  # 10% of canvas
#         logo = logo.resize(logo_size, Image.LANCZOS)

#         logo_x = canvas_size[0] - logo_size[0] - 10  # Right margin
#         logo_y = 10  # Top margin
#         canvas.paste(logo, (logo_x, logo_y), logo)

#     image_bytes = io.BytesIO()
#     canvas.save(image_bytes, format="PNG")
#     image_bytes.seek(0)

#     return image_bytes


def cad_file_process(image_path, canvas_size=(1000, 1000), margin_ratio=0.1):
    img = Image.open(image_path).convert("RGBA")
    logo_path = os.path.join(settings.BASE_DIR, "static/images/guyal_logo.png")

    margin = int(canvas_size[0] * margin_ratio)
    new_size = (canvas_size[0] - 2 * margin, canvas_size[1] - 2 * margin)

    img = img.resize(new_size, Image.LANCZOS)

    canvas_temp = Image.new("RGBA", canvas_size, "white")
    canvas = ImageOps.expand(canvas_temp, border=5, fill="black")
    paste_position = (margin, margin)
    canvas.paste(img, paste_position)

    logo = Image.open(logo_path).convert("RGBA")
    logo_size = (int(canvas_size[0] * 0.1), int(canvas_size[0] * 0.1))
    logo = logo.resize(logo_size, Image.LANCZOS)

    logo_margin = int(canvas_size[0] * 0.01)
    logo_position = (canvas_size[0] - logo_size[0] - logo_margin, logo_margin)

    canvas.paste(logo, logo_position, logo)

    image_bytes = io.BytesIO()
    canvas.save(image_bytes, format="PNG")
    image_bytes.seek(0)

    return image_bytes


def cad_file_view(request, order_id):
    order = Order.objects.get(order_id=order_id)
    if not order.cad_file:
        return HttpResponse("No CAD file available", status=404)

    cad_image = cad_file_process(order.cad_file.path)

    response = HttpResponse(cad_image, content_type="image/jpg")
    response["Content-Disposition"] = f'attachment; filename="cad_file_{order_id}.jpg"'
    return response


def export_orders_csv(request):
    response = HttpResponse(content_type="text/csv")
    today = datetime.today().strftime("%Y_%m_%d")

    response["Content-Disposition"] = f'attachment; filename="orders_{today}.csv"'

    writer = csv.writer(response)
    writer.writerow(
        [
            "Order ID",
            "Jewellery Type",
            "Order Details",
            "Customer",
            "Manufacturing Cost",
            "Margin",
            "Created At",
            "Updated At",
            "Deleted At",
        ]
    )

    orders = Order.objects.all().values_list(
        "order_id",
        "jewellery_type",
        "order_details",
        "customer__username",
        "manufacturing_cost",
        "margin",
        "created_at",
        "updated_at",
        "deleted_at",
    )

    for order in orders:
        writer.writerow(order)

    return response


def export_orders_xlsx(request):
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    today = datetime.today().strftime("%Y_%m_%d")
    response["Content-Disposition"] = f'attachment; filename="orders_{today}.xlsx"'

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Orders"

    headers = [
        "Order ID",
        "Jewellery Type",
        "Order Details",
        "Customer",
        "Manufacturing Cost",
        "Margin",
        "Created At",
        "Updated At",
        "Deleted At",
    ]
    ws.append(headers)

    orders = Order.objects.all()

    for order in orders:
        created_at_naive = localtime(order.created_at).replace(tzinfo=None)
        updated_at_naive = localtime(order.updated_at).replace(tzinfo=None)
        deleted_at_naive = localtime(order.deleted_at).replace(tzinfo=None)
        ws.append(
            [
                order.order_id,
                order.jewellery_type,
                order.order_details,
                order.customer.username,
                order.manufacturing_cost,
                order.margin,
                created_at_naive,
                updated_at_naive,
                deleted_at_naive,
            ]
        )

    wb.save(response)
    return response


def import_orders(request):
    if request.method == "POST":
        csv_file = request.FILES.get("csv_file")

        if not csv_file:
            messages.error(request, "Please upload a CSV file.")
            return redirect("order_list")

        if not csv_file.name.endswith(".csv"):
            messages.error(request, "Invalid file format. Please upload a CSV file.")
            return redirect("order_list")

        try:
            decoded_file = csv_file.read().decode("utf-8").splitlines()
            reader = csv.DictReader(decoded_file)

            success_count = 0
            skipped_count = 0

            for row in reader:
                customer = User.objects.filter(
                    username=row["customer_username"]
                ).first()

                if not customer:
                    skipped_count += 1
                    continue

                Order.objects.create(
                    jewellery_type=row["jewellery_type"],
                    order_details=row["order_details"],
                    manufacturing_cost=(
                        int(row["manufacturing_cost"])
                        if row["manufacturing_cost"]
                        else None
                    ),
                    margin=int(row["margin"]) if row["margin"] else None,
                    customer=customer,
                )
                success_count += 1

            if success_count:
                messages.success(
                    request, f"Successfully imported {success_count} orders."
                )

            if skipped_count:
                messages.warning(
                    request,
                    f"Skipped {skipped_count} orders because users were not found.",
                )

        except Exception as e:
            messages.error(request, f"Error importing file: {str(e)}")

    return redirect("order_table")
