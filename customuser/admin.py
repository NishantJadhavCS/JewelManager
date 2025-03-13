from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django import forms


class CustomUserCreationForm(UserCreationForm):
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(), required=False, label="Assign Group"
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "group")

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            if self.cleaned_data["group"]:
                user.groups.set([self.cleaned_data["group"]])
        return user


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2", "group"),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if "group" in form.cleaned_data and form.cleaned_data["group"]:
            obj.groups.set([form.cleaned_data["group"]])


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
