import csv
from django.http import HttpResponse
from django.contrib import admin
from django.urls import path
from django.utils.html import format_html
from django.utils.timezone import now
from django.shortcuts import redirect
from .models import Order
from django.contrib.auth.models import User, Group
from guardian.shortcuts import get_objects_for_user
from django.http import HttpResponseForbidden
from django.urls import reverse
from import_export.admin import ExportMixin, ImportMixin
from import_export.formats.base_formats import CSV, XLSX
from .resources import OrderResource


class DeletedFilter(admin.SimpleListFilter):
    title = "Deleted Status"
    parameter_name = "deleted_status"

    def lookups(self, request, model_admin):
        return [
            ("deleted", "Deleted"),
            ("not_deleted", "Not Deleted"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "deleted":
            return queryset.exclude(deleted_at=None)
        if self.value() == "not_deleted":
            return queryset.filter(deleted_at=None)
        return queryset


@admin.register(Order)
class OrderAdmin(ExportMixin, ImportMixin, admin.ModelAdmin):
    resource_class = OrderResource
    search_fields = ("order_id", "jewellery_type")
    list_filter = ("jewellery_type", DeletedFilter)
    actions = ["soft_delete_orders", "restore_orders", "export_orders_to_csv"]

    autocomplete_fields = ["customer"]

    def get_list_display(self, request):
        """Customize displayed columns based on user groups."""
        columns = [
            "order_id",
            "jewellery_type",
            "created_at",
        ]

        if request.user.groups.filter(name="Customer").exists():
            columns.insert(2, "total_price_display")
        else:
            if not request.user.groups.filter(name="Factory Manager").exists():
                columns.insert(2, "margin")

            columns.insert(2, "manufacturing_cost")
            columns.insert(4, "is_deleted_display")

        if not request.user.groups.filter(
            name__in=["Factory Manager", "Customer"]
        ).exists():
            columns.insert(2, "customer")

        return columns

    def total_price_display(self, obj):
        if obj.manufacturing_cost and obj.margin is not None:
            return obj.manufacturing_cost + (obj.manufacturing_cost * obj.margin / 100)
        return "N/A"

    total_price_display.short_description = "Total Price"

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        if request.user.groups.filter(name="Customer").exists():
            return qs.filter(customer=request.user)

        return qs

    def soft_delete_button(self, obj):
        if (
            obj
            and hasattr(obj, "_request")
            and obj._request.user.groups.filter(name="Customer").exists()
        ):
            return ""
        elif not obj.is_deleted():
            return format_html(
                '<a class="button" href="{}">Soft Delete</a>',
                f"/admin/storemanager/order/{obj.order_id}/soft-delete/",
            )
        return "Already deleted"

    soft_delete_button.short_description = "Soft Delete"

    def response_change(self, request, obj):
        return redirect(reverse("admin:storemanager_order_change", args=[obj.pk]))

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))

        if request.user.groups.filter(name="Customer").exists():
            fields.append("total_price_display")
            fields.append("customer")
            return fields + ["manufacturing_cost", "margin"]

        if not request.user.groups.filter(name="Customer").exists():
            fields.append("soft_delete_button")

        if request.user.groups.filter(name="Factory Manager").exists():
            all_fields = [f.name for f in obj._meta.fields] if obj else []
            readonly = [
                field
                for field in all_fields
                if field not in ["cad_file", "manufacturing_cost"]
            ]
            return readonly
        return fields

    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        if "deleted_at" in fields:
            fields.remove("deleted_at")
        if (
            request.user.groups.filter(name="Factory Manager").exists()
            or request.user.groups.filter(name="Customer").exists()
        ):
            fields.remove("margin")
            fields.remove("customer")

        if request.user.groups.filter(name="Customer").exists():
            fields = [
                field
                for field in fields
                if field not in ["manufacturing_cost", "margin"]
            ]
            if "total_price_display" not in fields:
                fields.append("total_price_display")
        return fields

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<path:object_id>/soft-delete/",
                self.soft_delete_view,
                name="order_soft_delete",
            ),
        ]
        return custom_urls + urls

    def soft_delete_view(self, request, object_id):
        order = self.get_object(request, object_id)
        if order and not order.is_deleted():
            order.soft_delete()
        return redirect(request.META.get("HTTP_REFERER", "/admin/storemanager/order/"))

    def is_deleted_display(self, obj):
        return "Yes" if obj.is_deleted() else "No"

    is_deleted_display.short_description = "Deleted"

    def soft_delete_orders(self, request, queryset):
        queryset.update(deleted_at=now())

    soft_delete_orders.short_description = "Soft delete selected orders"

    def restore_orders(self, request, queryset):
        queryset.update(deleted_at=None)

    restore_orders.short_description = "Restore selected orders"

    def has_delete_permission(self, request, obj=None):
        return False

    def history_view(self, request, object_id, extra_context=None):
        if request.user.groups.filter(name="Customer").exists():
            return HttpResponseForbidden("You do not have permission to view history.")
        return super().history_view(request, object_id, extra_context)

    def get_export_formats(self):
        return [CSV, XLSX]
