from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import Order, User


class OrderResource(resources.ModelResource):
    customer_name = fields.Field(
        column_name="Customer Name",
        attribute="customer",
        widget=ForeignKeyWidget(User, field="username"),
    )

    class Meta:
        model = Order
        fields = (
            "order_id",
            "jewellery_type",
            "order_details",
            "customer_name",
            "manufacturing_cost",
            "margin",
            "created_at",
            "updated_at",
            "deleted_at",
        )
        exclude = (
            "order_id",
            "sketch",
            "cad_file",
            "created_at",
            "updated_at",
            "deleted_at",
        )

class OrderExportResource(resources.ModelResource):
    customer_name = fields.Field(
        column_name="Customer Name",
        attribute="customer",
        widget=ForeignKeyWidget(User, field="username"),
    )

    class Meta:
        model = Order
        fields = (
            "order_id",
            "jewellery_type",
            "order_details",
            "customer_name",
            "manufacturing_cost",
            "margin",
            "created_at",
            "updated_at",
            "deleted_at",
        )
        export_order = fields