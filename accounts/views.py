from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

def is_admin(user):
    return user.role == 'admin'

def login_view(request):
    if request.method == "POST":
        u = request.POST['username']
        p = request.POST['password']
        user = authenticate(request, username=u, password=p)
        if user:
            login(request, user)
            return redirect("admin_dashboard" if user.role=="admin" else "user_dashboard")
        messages.error(request, "Invalid credentials")
    return render(request, "login.html")

@login_required
def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    return render(request, "admin_dashboard.html")

@login_required
def user_dashboard_redirect(request):
    return redirect("user_dashboard")
