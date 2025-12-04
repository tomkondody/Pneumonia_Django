from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),

    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/toggle/<int:user_id>/", views.toggle_user, name="toggle_user"),
    path("admin/delete/<int:user_id>/", views.delete_user, name="delete_user"),
]
