from django.urls import path
from . import views

urlpatterns = [
    path("admin/order-table/", views.order_table_view, name="order_table"),
    path(
        "admin/order-table/pdf/<int:order_id>/",
        views.generate_order_pdf,
        name="generate_order_pdf",
    ),
    path("export-orders-csv/", views.export_orders_csv, name="export_orders_csv"),
    path("export-orders-xlsx/", views.export_orders_xlsx, name="export_orders_xlsx"),
    path("import-orders/", views.import_orders, name="import_orders"),
    path("generate-cad/<int:order_id>/", views.cad_file_view, name="generate_cad"),
]
