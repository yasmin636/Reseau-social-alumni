from django.urls import path
from . import views

urlpatterns = [
    path("connexion-admin/", views.admin_login_view, name="admin_login"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register, name="register"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-dashboard/users/<int:user_id>/toggle-active/", views.admin_user_toggle_active, name="admin_user_toggle_active"),
    path("admin-dashboard/users/<int:user_id>/", views.admin_user_detail, name="admin_user_detail"),
    path("admin-dashboard/users/<int:user_id>/delete/", views.admin_user_delete, name="admin_user_delete"),
    path("admin-dashboard/users/<int:user_id>/change-role/", views.admin_user_change_role, name="admin_user_change_role"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("dashboard-etudiant/", views.dashboard_etudiant, name="dashboard_etudiant"),
    path("dashboard-alumni/", views.dashboard_alumni, name="dashboard_alumni"),
    path("post/create/", views.post_create, name="post_create"),
    path("offres/", views.offres, name="offres"),
    path("favoris/", views.favoris, name="favoris"),
    path("notifications/", views.notifications, name="notifications"),
    path("post/<int:post_id>/like/", views.post_like, name="post_like"),
    path("post/<int:post_id>/favori/", views.post_favori, name="post_favori"),
    path("post/<int:post_id>/commenter/", views.post_commenter, name="post_commenter"),
    path("chat/", views.chat_page, name="chat_page"),
    path("chat/<int:user_id>/", views.chat_page, name="chat_avec"),
    path("chat/<int:alumni_id>/envoyer/", views.chat_envoyer, name="chat_envoyer"),
    path("chat/<int:alumni_id>/messages/", views.chat_messages, name="chat_messages"),
    path("profil/", views.profil_etudiant, name="profil_etudiant"),
    path("profil-alumni/", views.profil_alumni, name="profil_alumni"),
]