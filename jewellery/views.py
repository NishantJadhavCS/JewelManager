from django.shortcuts import redirect, render


def redirect_to_admin(request):
    return redirect("/admin/")
