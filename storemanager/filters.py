import django_filters
from .models import Order
from django.contrib.auth.models import User


class OrderFilter(django_filters.FilterSet):
    order_id = django_filters.CharFilter(
        lookup_expr="icontains", label="Search Order ID"
    )
    jewellery_type = django_filters.ChoiceFilter(
        choices=Order.JEWELLERY_CHOICES, label="Jewellery Type"
    )
    customer = django_filters.CharFilter(
        field_name="customer__username",
        lookup_expr="icontains",
        label="Customer (Search by username)",
    )
    deleted_status = django_filters.ChoiceFilter(
        label="Deleted Status",
        choices=[("deleted", "Deleted"), ("active", "Active")],
        method="filter_deleted_status",
    )

    def filter_deleted_status(self, queryset, name, value):
        if value == "deleted":
            return queryset.exclude(deleted_at=None)
        return queryset.filter(deleted_at=None)

    class Meta:
        model = Order
        fields = ["order_id", "jewellery_type", "customer"]
