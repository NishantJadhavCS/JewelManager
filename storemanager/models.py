from django.contrib.auth.models import User, Group
from django.db import models
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils.timezone import now
from guardian.shortcuts import assign_perm


def sketch_upload_path(instance, filename):
    return f"orders/{instance.pk}/sketch/{filename}"


def cad_upload_path(instance, filename):
    return f"orders/{instance.pk}/cad/{filename}"


class Order(models.Model):
    JEWELLERY_CHOICES = [
        ("Rings", "Rings"),
        ("Pendants", "Pendants"),
        ("Earrings", "Earrings"),
        ("Charms", "Charms"),
        ("Bracelets", "Bracelets"),
    ]
    order_id = models.AutoField(primary_key=True)
    jewellery_type = models.CharField(
        max_length=50,
        choices=JEWELLERY_CHOICES,
        default="Rings",
    )
    order_details = models.TextField()
    sketch = models.ImageField(
        upload_to=sketch_upload_path, verbose_name="Sketch Image", null=True
    )
    cad_file = models.FileField(
        upload_to=cad_upload_path, null=True, blank=True, verbose_name="CAD File"
    )
    manufacturing_cost = models.IntegerField(null=True, blank=True)
    margin = models.IntegerField(null=True, blank=True)

    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"groups__name": "Customer"},
        related_name="orders",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def soft_delete(self):
        self.deleted_at = now()
        self.save(update_fields=["deleted_at"])

    def restore(self):
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])

    def is_deleted(self):
        return self.deleted_at is not None

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and self.sketch:
            self._move_file_to_correct_path("sketch", sketch_upload_path)

        if is_new and self.cad_file:
            self._move_file_to_correct_path("cad_file", cad_upload_path)

        if is_new and self.customer:
            assign_perm("storemanager.view_order", self.customer, self)

        super().save(update_fields=["sketch", "cad_file"])

    def _move_file_to_correct_path(self, field_name, upload_path_func):
        file_field = getattr(self, field_name)
        if not file_field:
            return
        new_path = upload_path_func(self, os.path.basename(file_field.name))
        old_path = file_field.name
        new_file = default_storage.save(new_path, ContentFile(file_field.read()))

        setattr(self, field_name, new_file)
        default_storage.delete(old_path)

    def __str__(self):
        return f"Order {self.order_id} - {self.jewellery_type}"
