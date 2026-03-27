from django.urls import path
from . import views


urlpatterns = [

    # Dashboard principal
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),

    # Dashboards selon rôle
    path("dashboard-etudiant/", views.dashboard_etudiant, name="dashboard_etudiant"),
    path("dashboard-alumni/", views.dashboard_alumni, name="dashboard_alumni"),

    # Posts
    path("post/create/", views.post_create, name="post_create"),

    # Offres / favoris / notifications
    path("offres/", views.offres, name="offres"),
    path("favoris/", views.favoris, name="favoris"),
    path("notifications/", views.notifications, name="notifications"),

    # Authentification
    path("login/", views.login_view, name="login"),
    path("register/", views.register, name="register"),
]