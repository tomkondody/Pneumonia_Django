from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import CustomUser


def is_admin(user):
    return user.is_authenticated and user.role == "admin"


def register_view(request):
    if request.method == "POST":
        u = request.POST.get("username")
        p = request.POST.get("password")

        if CustomUser.objects.filter(username=u).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        # Create user as DISABLED until admin approves
        user = CustomUser.objects.create_user(
            username=u,
            password=p,
            role="user",
            is_active=False       # 🔥 NOT ACTIVE UNTIL APPROVED
        )

        messages.success(request, "Registration successful. Waiting for admin approval.")
        return redirect("login")

    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        u = request.POST.get("username")
        p = request.POST.get("password")
        user = authenticate(request, username=u, password=p)

        if user:
            # Check ACTIVATION
            if not user.is_active:
                messages.error(request, "Your account is not approved by admin yet.")
                return redirect("login")

            login(request, user)
            return redirect("admin_dashboard" if user.role == "admin" else "user_dashboard")

        messages.error(request, "Invalid username or password")
    return render(request, "login.html")


@login_required(login_url="login")
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required(login_url="login")
@user_passes_test(is_admin, login_url="home")
def admin_dashboard(request):
    users = CustomUser.objects.exclude(role="admin")

    # Split approved/pending
    approved = CustomUser.objects.filter(is_active=True, role="user")
    pending  = CustomUser.objects.filter(is_active=False, role="user")

    return render(request, "admin_dashboard.html", {
        "approved": approved,
        "pending": pending
    })


@login_required(login_url="login")
@user_passes_test(is_admin, login_url="home")
def toggle_user(request, user_id):
    u = CustomUser.objects.get(id=user_id)
    u.is_active = not u.is_active
    u.save()
    return redirect("admin_dashboard")


@login_required(login_url="login")
@user_passes_test(is_admin, login_url="home")
def delete_user(request, user_id):
    u = CustomUser.objects.get(id=user_id)
    u.delete()
    return redirect("admin_dashboard")
