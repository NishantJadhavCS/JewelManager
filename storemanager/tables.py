import django_tables2 as tables
from .models import Order
from django.utils.html import format_html
from django.urls import reverse


class OrderTable(tables.Table):
    deleted_status = tables.Column(
        empty_values=(), verbose_name="Deleted Status", orderable=False
    )
    pdf = tables.Column(empty_values=(), verbose_name="PDF")
    img = tables.Column(empty_values=(), verbose_name="Image")

    class Meta:
        model = Order
        template_name = "django_tables2/bootstrap4.html"
        fields = (
            "order_id",
            "jewellery_type",
            "order_details",
            "manufacturing_cost",  
            "margin",  
            "customer",  
            "created_at",
        )
        order_by = "created_at"

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        hidden_columns = set(["deleted_status"])  # Hide Deleted Status for everyone

        if user:
            if user.groups.filter(name="Customer").exists():
                hidden_columns.update(
                    ["manufacturing_cost", "margin", "customer"]
                )  # Hide for Customers
            elif user.groups.filter(name="Factory Manager").exists():
                hidden_columns.update(
                    ["margin", "customer"]
                )  # Hide for Factory Managers

        self.exclude = tuple(hidden_columns)  # Apply column exclusions dynamically

    def render_deleted_status(self, value, record):
        return "Deleted" if record.deleted_at else "Active"

    def render_pdf(self, record):
        pdf_url = reverse("generate_order_pdf", kwargs={"order_id": record.order_id})
        return format_html(
            '<a href="{}" class="btn btn-primary btn-sm" target="_blank">Generate PDF</a>',
            pdf_url,
        )

    def render_img(self, record):
        img_url = reverse("generate_cad", kwargs={"order_id": record.pk})
        return format_html(
            '<a href="{}" class="btn btn-primary btn-sm" target="_blank">Generate CAD</a>',
            img_url,
        )

