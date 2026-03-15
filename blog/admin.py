from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import Post, Comment, Profile


# ===============================
# INLINE PROFILE dans USER ADMIN
# ===============================
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profil'
    fields = ('role', 'photo', 'annee_actuelle', 'filiere', 'compte_active')
    readonly_fields = ('apercu_photo',)

    def apercu_photo(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" width="80" height="80" '
                'style="border-radius:50%;object-fit:cover;border:2px solid #00acc1;" />',
                obj.photo.url
            )
        return "Aucune photo"
    apercu_photo.short_description = "Aperçu"


# ===============================
# USER ADMIN PERSONNALISÉ
# ===============================
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)

    list_display = (
        'photo_profil',
        'username',
        'email',
        'first_name',
        'last_name',
        'get_role',
        'get_filiere',
        'get_statut_compte',
        'is_staff',
    )

    list_display_links = ('username',)

    def photo_profil(self, obj):
        try:
            if obj.profile.photo:
                return format_html(
                    '<img src="{}" width="38" height="38" '
                    'style="border-radius:50%;object-fit:cover;'
                    'border:2px solid #00acc1;" />',
                    obj.profile.photo.url
                )
        except Profile.DoesNotExist:
            pass
        # Initiale si pas de photo
        couleurs = ['#e53935','#8e24aa','#1e88e5','#00897b','#f4511e']
        couleur = couleurs[hash(obj.username) % len(couleurs)]
        return format_html(
            '<div style="width:38px;height:38px;border-radius:50%;'
            'background:{};display:inline-flex;align-items:center;'
            'justify-content:center;color:white;font-weight:bold;'
            'font-size:16px;">{}</div>',
            couleur,
            obj.username[0].upper()
        )
    photo_profil.short_description = '📷'

    def get_role(self, obj):
        try:
            role = obj.profile.role
            if role == 'etudiant':
                return format_html(
                    '<span style="background:#1a73e8;color:white;'
                    'padding:3px 10px;border-radius:12px;font-size:12px;">'
                    '🎓 Étudiant</span>'
                )
            elif role == 'alumni':
                return format_html(
                    '<span style="background:#34a853;color:white;'
                    'padding:3px 10px;border-radius:12px;font-size:12px;">'
                    '🏆 Alumni</span>'
                )
        except Profile.DoesNotExist:
            pass
        return format_html('<span style="color:#999;">—</span>')
    get_role.short_description = 'Type'

    def get_filiere(self, obj):
        try:
            return obj.profile.filiere or '—'
        except Profile.DoesNotExist:
            return '—'
    get_filiere.short_description = 'Filière'

    def get_statut_compte(self, obj):
        try:
            if obj.is_staff or obj.is_superuser:
                return format_html(
                    '<span style="background:#607d8b;color:white;'
                    'padding:3px 10px;border-radius:12px;font-size:12px;">'
                    '⚙️ Admin</span>'
                )
            if obj.profile.compte_active:
                return format_html(
                    '<span style="background:#34a853;color:white;'
                    'padding:3px 10px;border-radius:12px;font-size:12px;">'
                    '✅ Actif</span>'
                )
            else:
                return format_html(
                    '<span style="background:#e53935;color:white;'
                    'padding:3px 10px;border-radius:12px;font-size:12px;">'
                    '⏳ En attente</span>'
                )
        except Profile.DoesNotExist:
            return '—'
    get_statut_compte.short_description = 'Statut compte'

    # Filtre par rôle et statut dans la sidebar
    list_filter = UserAdmin.list_filter + ('profile__role', 'profile__compte_active')

    # Action pour activer/désactiver des comptes en masse
    actions = ['activer_comptes', 'desactiver_comptes']

    def activer_comptes(self, request, queryset):
        for user in queryset:
            try:
                user.profile.compte_active = True
                user.profile.save()
            except Profile.DoesNotExist:
                pass
        self.message_user(request, f"{queryset.count()} compte(s) activé(s).")
    activer_comptes.short_description = "✅ Activer les comptes sélectionnés"

    def desactiver_comptes(self, request, queryset):
        for user in queryset:
            try:
                user.profile.compte_active = False
                user.profile.save()
            except Profile.DoesNotExist:
                pass
        self.message_user(request, f"{queryset.count()} compte(s) désactivé(s).")
    desactiver_comptes.short_description = "❌ Désactiver les comptes sélectionnés"


# ===============================
# POST ADMIN
# ===============================
class PostAdmin(admin.ModelAdmin):
    list_display = ('titre', 'auteur', 'date_creation', 'status')
    list_filter = ('status', 'date_creation')
    search_fields = ['titre', 'contenu']


# ===============================
# COMMENT ADMIN
# ===============================
class CommentAdmin(admin.ModelAdmin):
    list_display = ('auteur', 'contenu', 'date_creation', 'actif')
    list_filter = ('actif', 'date_creation')
    search_fields = ['contenu']


# ===============================
# ENREGISTREMENT
# ===============================
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Profile)