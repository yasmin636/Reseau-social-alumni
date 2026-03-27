from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path("connexion-admin/", views.admin_login_view, name="admin_login"),
    path("admin-logout/", views.admin_logout_view, name="admin_logout"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),

    # Admin dashboard
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-dashboard/users/<int:user_id>/", views.admin_user_detail, name="admin_user_detail"),
    path("admin-dashboard/users/<int:user_id>/toggle-active/", views.admin_user_toggle_active, name="admin_user_toggle_active"),
    path("admin-dashboard/users/<int:user_id>/delete/", views.admin_user_delete, name="admin_user_delete"),
    path("admin-dashboard/users/<int:user_id>/change-role/", views.admin_user_change_role, name="admin_user_change_role"),

    # Admin — Posts
    path("admin-dashboard/posts/<int:post_id>/delete/", views.admin_post_delete, name="admin_post_delete"),
    path("admin-dashboard/posts/<int:post_id>/approve/", views.admin_post_approve, name="admin_post_approve"),

    # Admin — Offres
    path("admin-dashboard/offres/<int:offre_id>/approve/", views.admin_offre_approve, name="admin_offre_approve"),
    path("admin-dashboard/offres/<int:offre_id>/delete/", views.admin_offre_delete, name="admin_offre_delete"),

    # Dashboards
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("dashboard-etudiant/", views.dashboard_etudiant, name="dashboard_etudiant"),
    path("dashboard-alumni/", views.dashboard_alumni, name="dashboard_alumni"),

    # Posts
    path("post/create/", views.post_create, name="post_create"),
    path("posts/", views.posts_etudiant, name="posts_etudiant"),
    path("mes-posts/", views.mes_posts, name="mes_posts"),
    path("post/<int:post_id>/like/", views.post_like, name="post_like"),
    path("post/<int:post_id>/favori/", views.post_favori, name="post_favori"),
    path("post/<int:post_id>/commenter/", views.post_commenter, name="post_commenter"),
    path("post/<int:post_id>/stats/", views.post_stats, name="post_stats"),

    # ✅ Suppression commentaire POST — une seule route, cohérente avec le JS
    path("comment/<int:comment_id>/supprimer/", views.comment_supprimer, name="comment_supprimer"),

    # Offres
    path("offres/", views.offres, name="offres"),
    path("offre/create/", views.offre_create, name="offre_create"),
    path("mes-offres/", views.mes_offres, name="mes_offres"),
    path("offre/<int:offre_id>/like/", views.offre_like, name="offre_like"),
    path("offre/<int:offre_id>/favori/", views.offre_favori, name="offre_favori"),
    path("offre/<int:offre_id>/stats/", views.offre_stats, name="offre_stats"),
    path("offre/<int:offre_id>/commenter/", views.offre_commenter, name="offre_commenter"),

    # ✅ Suppression commentaire OFFRE — URL alignée avec le JS : /offre/comment/<id>/supprimer/
    path("offre/comment/<int:comment_id>/supprimer/", views.offre_comment_supprimer, name="offre_comment_supprimer"),

    # Autres
    path("favoris/", views.favoris, name="favoris"),
    path("notifications/", views.notifications, name="notifications"),
    path("profil/", views.profil_etudiant, name="profil_etudiant"),
    path("profil-alumni/", views.profil_alumni, name="profil_alumni"),
    path("profil/changer-mot-de-passe/", views.changer_mot_de_passe, name="changer_mot_de_passe"),
    path("chat/", views.chat_page, name="chat_page"),
    path("chat/<int:user_id>/", views.chat_page, name="chat_avec"),
    path("chat/<int:alumni_id>/envoyer/", views.chat_envoyer, name="chat_envoyer"),
    path("chat/<int:alumni_id>/messages/", views.chat_messages, name="chat_messages"),
    path("fil-alumni/", views.fil_alumni, name="fil_alumni"),
    path("fil-etudiant/", views.fil_etudiant, name="fil_etudiant"),
]