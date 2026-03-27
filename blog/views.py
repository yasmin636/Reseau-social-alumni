from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.db.models import Q, Max
from .models import Post, Comment, Profile, Notification, Message, Like, Favori
from .forms import CommentForm, PostForm, RegisterForm, RegisterAlumniForm

def is_admin(user):
    return user.is_staff or user.is_superuser

def admin_login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_staff or user.is_superuser:
                login(request, user)
                return redirect("admin_dashboard")
            else:
                return render(request, "admin_login.html", {"error": "Vous n'avez pas les droits administrateur."})
        else:
            return render(request, "admin_login.html", {"error": "Nom d'utilisateur ou mot de passe incorrect."})
    return render(request, "admin_login.html")

def admin_logout_view(request):
    logout(request)
    return redirect("admin_login")

def logout_view(request):
    logout(request)
    return redirect("login")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user_type = request.POST.get("user_type", "etudiant")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_staff or user.is_superuser:
                return render(request, "login.html", {"error": "Utilisez la page de connexion administrateur."})
            try:
                profile = user.profile
            except Profile.DoesNotExist:
                profile = Profile.objects.create(user=user, role='etudiant', compte_active=False)
            if user_type == "etudiant" and profile.role != "etudiant":
                return render(request, "login.html", {
                    "error": "Ce compte est un compte Alumni. Veuillez sélectionner Alumni.",
                    "user_type": user_type
                })
            if user_type == "alumni" and profile.role != "alumni":
                return render(request, "login.html", {
                    "error": "Ce compte est un compte Étudiant. Veuillez sélectionner Étudiant.",
                    "user_type": user_type
                })
            if not profile.compte_active:
                return render(request, "login.html", {"error": "pending", "user_type": user_type})
            login(request, user)
            if profile.role == "etudiant":
                return redirect("dashboard_etudiant")
            elif profile.role == "alumni":
                return redirect("dashboard_alumni")
            return redirect("mes_posts")
        else:
            return render(request, "login.html", {
                "error": "Nom d'utilisateur ou mot de passe incorrect.",
                "user_type": user_type
            })
    return render(request, "login.html")

def register(request):
    user_type = request.POST.get("user_type", "etudiant")
    if request.method == "POST":
        if user_type == "alumni":
            form = RegisterAlumniForm(request.POST)
        else:
            form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['prenom'],
                last_name=form.cleaned_data['nom'],
            )
            user.is_active = True
            user.save()
            if user_type == "alumni":
                Profile.objects.create(user=user, role='alumni',
                    annee_licence=form.cleaned_data['annee_licence'],
                    filiere_alumni=form.cleaned_data['filiere_alumni'],
                    en_poste=form.cleaned_data.get('en_poste', False),
                    compte_active=False)
            else:
                Profile.objects.create(user=user, role='etudiant',
                    annee_actuelle=form.cleaned_data['annee_actuelle'],
                    filiere=form.cleaned_data['filiere'],
                    compte_active=False)
            nom = f"{form.cleaned_data['prenom']} {form.cleaned_data['nom']}"
            for admin_user in User.objects.filter(is_staff=True):
                Notification.objects.create(destinataire=admin_user,
                    message=f"Nouveau compte en attente de validation : {nom} ({user_type})")
            return render(request, "register.html", {"success": True, "user_type": user_type, "nom_complet": nom})
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form, "user_type": user_type})

@user_passes_test(is_admin)
def admin_dashboard(request):
    from .models import Offre
    users = User.objects.select_related("profile").all().order_by("date_joined")
    pending_posts = Post.objects.filter(status=0).select_related("auteur").order_by("-date_creation")
    pending_offres = Offre.objects.filter(status=0).select_related("auteur").order_by("-date_creation")
    all_posts = Post.objects.all().select_related("auteur").order_by("-date_creation")
    all_offres = Offre.objects.all().select_related("auteur").order_by("-date_creation")
    alumni_count = Profile.objects.filter(role="alumni").count()
    pending_users = []
    for u in users:
        try:
            if not u.profile.compte_active and not u.is_staff:
                pending_users.append(u)
        except Profile.DoesNotExist:
            pass
    return render(request, "admin.html", {
        "users": users,
        "pending_posts": pending_posts,
        "pending_offres": pending_offres,
        "all_posts": all_posts,
        "all_offres": all_offres,
        "alumni_count": alumni_count,
        "last_messages": [],
        "pending_users": pending_users,
    })


# ============================================================
# ✅ CORRECTION : admin_post_delete
# Supprime le post + notifie l'auteur alumni
# Grâce au CASCADE dans models.py, tous les likes, favoris
# et commentaires liés sont supprimés automatiquement
# → disparaît du fil alumni ET étudiant immédiatement
# ============================================================
@user_passes_test(is_admin)
def admin_post_delete(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    auteur = post.auteur
    titre = post.titre or "Sans titre"

    post.delete()  # CASCADE → supprime likes, favoris, comments liés

    # Notifier l'auteur alumni que son post a été supprimé
    Notification.objects.create(
        destinataire=auteur,
        message=f"Votre post « {titre} » a été supprimé par l'administrateur."
    )

    return redirect("admin_dashboard")


@user_passes_test(is_admin)
def admin_post_approve(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post.status = 1
    post.save()
    etudiants = User.objects.filter(profile__role='etudiant', profile__compte_active=True)
    for etudiant in etudiants:
        Notification.objects.create(
            destinataire=etudiant,
            message=f"Nouveau post de {post.auteur.get_full_name() or post.auteur.username} : {post.titre or 'Sans titre'}"
        )
    return redirect("admin_dashboard")


@user_passes_test(is_admin)
def admin_offre_approve(request, offre_id):
    from .models import Offre
    offre = get_object_or_404(Offre, pk=offre_id)
    offre.status = 1
    offre.save()
    etudiants = User.objects.filter(profile__role='etudiant', profile__compte_active=True)
    for etudiant in etudiants:
        Notification.objects.create(
            destinataire=etudiant,
            message=f"Nouvelle offre de {offre.auteur.get_full_name() or offre.auteur.username} : {offre.titre} chez {offre.entreprise}"
        )
    Notification.objects.create(
        destinataire=offre.auteur,
        message=f"Votre offre « {offre.titre} » a été validée et est maintenant visible par les étudiants."
    )
    return redirect("admin_dashboard")


# ============================================================
# ✅ CORRECTION : admin_offre_delete
# Supprime l'offre + notifie l'auteur alumni
# Grâce au CASCADE dans models.py, tous les likes, favoris
# et commentaires liés sont supprimés automatiquement
# → disparaît du fil alumni ET étudiant immédiatement
# ============================================================
@user_passes_test(is_admin)
def admin_offre_delete(request, offre_id):
    from .models import Offre
    offre = get_object_or_404(Offre, pk=offre_id)
    auteur = offre.auteur
    titre = offre.titre

    offre.delete()  # CASCADE → supprime likes, favoris, comments liés

    # Notifier l'auteur alumni que son offre a été supprimée
    Notification.objects.create(
        destinataire=auteur,
        message=f"Votre offre « {titre} » a été supprimée par l'administrateur."
    )

    return redirect("admin_dashboard")


@user_passes_test(is_admin)
def admin_user_detail(request, user_id):
    u = get_object_or_404(User, pk=user_id)
    try:
        profile = u.profile
    except Profile.DoesNotExist:
        profile = None
    notif_message = request.session.pop('notif_message', None)
    return render(request, "admin_user_detail.html", {"u": u, "profile": profile, "notif_message": notif_message})

@user_passes_test(is_admin)
def admin_user_toggle_active(request, user_id):
    user_obj = get_object_or_404(User, pk=user_id)
    try:
        user_obj.profile.compte_active = not user_obj.profile.compte_active
        user_obj.profile.save()
        nom = user_obj.get_full_name() or user_obj.username
        if user_obj.profile.compte_active:
            Notification.objects.create(destinataire=user_obj, message="Votre compte a été activé. Vous pouvez maintenant vous connecter.")
            Notification.objects.create(destinataire=request.user, message=f"Vous avez autorisé {nom} à accéder à la plateforme.")
            request.session['notif_message'] = f"Le compte de {nom} a été activé avec succès."
        else:
            Notification.objects.create(destinataire=request.user, message=f"Vous avez désactivé le compte de {nom}.")
            request.session['notif_message'] = f"Le compte de {nom} a été désactivé."
    except Profile.DoesNotExist:
        Profile.objects.create(user=user_obj, compte_active=True)
    return redirect("admin_user_detail", user_id=user_id)

@user_passes_test(is_admin)
def admin_user_delete(request, user_id):
    user_obj = get_object_or_404(User, pk=user_id)
    nom = user_obj.get_full_name() or user_obj.username
    user_obj.delete()
    Notification.objects.create(destinataire=request.user, message=f"Le compte de {nom} a été supprimé.")
    return redirect("admin_dashboard")

@user_passes_test(is_admin)
def admin_user_change_role(request, user_id):
    user_obj = get_object_or_404(User, pk=user_id)
    try:
        profile = user_obj.profile
        nom = user_obj.get_full_name() or user_obj.username
        if profile.role == "etudiant":
            profile.role = "alumni"
            msg = f"{nom} est maintenant Alumni."
        else:
            profile.role = "etudiant"
            msg = f"{nom} est maintenant Etudiant."
        profile.save()
        Notification.objects.create(destinataire=request.user, message=msg)
        request.session['notif_message'] = msg
    except Profile.DoesNotExist:
        pass
    return redirect("admin_user_detail", user_id=user_id)

class PostList(generic.ListView):
    queryset = Post.objects.filter(status=1).order_by("-date_creation")
    template_name = "index.html"

class DashboardView(generic.ListView):
    model = Post
    template_name = "blog/dashboard.html"
    context_object_name = "post_list"

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    comments = post.comments.filter(actif=True)
    new_comment = None
    if request.method == "POST":
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.auteur = request.user
            new_comment.save()
    else:
        comment_form = CommentForm()
    return render(request, "post_detail.html", {"post": post, "comments": comments, "new_comment": new_comment, "comment_form": comment_form})

@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.auteur = request.user
            post.status = 0
            post.save()
            for admin_user in User.objects.filter(is_staff=True):
                Notification.objects.create(
                    destinataire=admin_user,
                    message=f"Nouveau post en attente de validation de {request.user.get_full_name() or request.user.username} : {post.titre or 'Sans titre'}"
                )
            return redirect('dashboard_alumni')
    else:
        form = PostForm()
    return render(request, 'blog/post_create.html', {'form': form})

@login_required
def post_like(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
        if post.auteur != request.user:
            Notification.objects.create(
                destinataire=post.auteur,
                message=f"{request.user.get_full_name() or request.user.username} a aimé votre post : {post.titre}"
            )
            Notification.objects.create(
                destinataire=request.user,
                message=f"Vous avez aimé le post de {post.auteur.get_full_name() or post.auteur.username} : {post.titre}"
            )
    return JsonResponse({'liked': liked, 'total': post.likes.count()})

@login_required
def post_favori(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    favori, created = Favori.objects.get_or_create(post=post, user=request.user)
    if not created:
        favori.delete()
        en_favori = False
    else:
        en_favori = True
        Notification.objects.create(
            destinataire=request.user,
            message=f"Vous avez ajouté aux favoris le post de {post.auteur.get_full_name() or post.auteur.username} : {post.titre}"
        )
    return JsonResponse({'favoris': en_favori, 'total': post.favoris.count()})

@login_required
def post_commenter(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == "POST":
        contenu = request.POST.get("contenu", "").strip()
        if contenu:
            comment = Comment.objects.create(post=post, auteur=request.user, contenu=contenu, actif=True)
            if post.auteur != request.user:
                Notification.objects.create(
                    destinataire=post.auteur,
                    message=f"{request.user.get_full_name() or request.user.username} a commenté votre post : {post.titre}"
                )
                Notification.objects.create(
                    destinataire=request.user,
                    message=f"Vous avez commenté le post de {post.auteur.get_full_name() or post.auteur.username} : {post.titre}"
                )
            return JsonResponse({
                'success': True,
                'id': comment.id,
                'auteur': request.user.get_full_name() or request.user.username,
                'contenu': comment.contenu,
                'date': comment.date_creation.strftime("%d/%m/%Y à %H:%M")
            })
    return JsonResponse({'success': False})

@login_required
def post_stats(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    likers = post.likes.select_related('user').order_by('-id')[:3]
    comments = post.comments.filter(actif=True).select_related('auteur').order_by('date_creation')
    return JsonResponse({
        'nb_likes': post.likes.count(),
        'nb_favoris': post.favoris.count(),
        'nb_comments': post.comments.filter(actif=True).count(),
        'user_liked': post.likes.filter(user=request.user).exists(),
        'user_favori': post.favoris.filter(user=request.user).exists(),
        'likers': [l.user.get_full_name() or l.user.username for l in likers],
        'comments': [
            {
                'id': c.id,
                'auteur': c.auteur.get_full_name() or c.auteur.username,
                'auteur_username': c.auteur.username,
                'contenu': c.contenu,
                'date': c.date_creation.strftime("%d/%m à %H:%M")
            } for c in comments
        ],
    })

@login_required
def chat_page(request, user_id=None):
    messages_envoyes = Message.objects.filter(expediteur=request.user).values_list('destinataire', flat=True)
    messages_recus = Message.objects.filter(destinataire=request.user).values_list('expediteur', flat=True)
    contact_ids = set(list(messages_envoyes) + list(messages_recus))
    try:
        role = request.user.profile.role
    except:
        role = 'etudiant'
    if role == 'etudiant':
        contacts = User.objects.filter(id__in=contact_ids, profile__role='alumni')
    else:
        contacts = User.objects.filter(id__in=contact_ids)
    selected_user = None
    conversation = []
    if user_id:
        selected_user = get_object_or_404(User, pk=user_id)
        if role == 'etudiant' and selected_user.profile.role != 'alumni':
            return redirect('chat_page')
        conversation = Message.objects.filter(
            Q(expediteur=request.user, destinataire=selected_user) |
            Q(expediteur=selected_user, destinataire=request.user)
        ).order_by("date_envoi")
        conversation.filter(destinataire=request.user, lu=False).update(lu=True)
        if not Message.objects.filter(expediteur=request.user, destinataire=selected_user).exists():
            nom = request.user.get_full_name() or request.user.username
            Notification.objects.create(
                destinataire=selected_user,
                message=f"{nom} veut vous contacter via le chat."
            )
    tous_alumni = User.objects.filter(
        profile__role='alumni',
        profile__compte_active=True
    ).exclude(id=request.user.id)
    return render(request, "blog/chat.html", {
        "contacts": contacts,
        "selected_user": selected_user,
        "conversation": conversation,
        "tous_alumni": tous_alumni,
    })

@login_required
def chat_envoyer(request, alumni_id):
    destinataire = get_object_or_404(User, pk=alumni_id)
    if request.method == "POST":
        contenu = request.POST.get("contenu", "").strip()
        if contenu:
            Message.objects.create(expediteur=request.user, destinataire=destinataire, contenu=contenu)
            nom = request.user.get_full_name() or request.user.username
            Notification.objects.create(
                destinataire=destinataire,
                message=f"Nouveau message de {nom} : {contenu[:50]}"
            )
            return JsonResponse({'success': True, 'contenu': contenu, 'date': 'maintenant'})
    return JsonResponse({'success': False})

@login_required
def chat_messages(request, alumni_id):
    alumni = get_object_or_404(User, pk=alumni_id)
    msgs = Message.objects.filter(
        Q(expediteur=request.user, destinataire=alumni) |
        Q(expediteur=alumni, destinataire=request.user)
    ).order_by("date_envoi")
    data = [{'expediteur': m.expediteur.get_full_name() or m.expediteur.username,
              'contenu': m.contenu,
              'date': m.date_envoi.strftime("%d/%m/%Y à %H:%M"),
              'moi': m.expediteur == request.user} for m in msgs]
    return JsonResponse({'messages': data})

@login_required
def offres(request):
    from .models import Offre
    offres_list = Offre.objects.filter(status=1).order_by("-date_creation")
    return render(request, "blog/offres.html", {"offres_list": offres_list})

@login_required
def notifications(request):
    notifs = Notification.objects.filter(destinataire=request.user).order_by("-date_creation")
    notifs.update(lue=True)
    return render(request, "notifications.html", {"notifs": notifs})

@login_required
def dashboard_etudiant(request):
    from .models import Offre
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = None
    posts = Post.objects.filter(status=1).order_by("-date_creation")
    offres_qs = Offre.objects.filter(status=1).order_by("-date_creation")
    posts_data = []
    for post in posts:
        posts_data.append({
            'type': 'post',
            'obj': post,
            'auteur': post.auteur,
            'date': post.date_creation,
            'liked': post.likes.filter(user=request.user).exists(),
            'en_favori': post.favoris.filter(user=request.user).exists(),
            'nb_likes': post.likes.count(),
            'nb_favoris': post.favoris.count(),
            'nb_comments': post.comments.filter(actif=True).count(),
            'comments': post.comments.filter(actif=True),
        })
    offres_data = []
    for offre in offres_qs:
        offres_data.append({
            'type': 'offre',
            'obj': offre,
            'auteur': offre.auteur,
            'date': offre.date_creation,
            'nb_likes_offre': offre.likes.count(),
            'nb_favoris_offre': offre.favoris.count(),
            'liked_offre': offre.likes.filter(user=request.user).exists(),
            'en_favori_offre': offre.favoris.filter(user=request.user).exists(),
        })
    feed = sorted(posts_data + offres_data, key=lambda x: x['date'], reverse=True)
    nb_notifications = Notification.objects.filter(destinataire=request.user, lue=False).count()
    nb_offres = Offre.objects.filter(status=1).count()
    nb_alumni = Profile.objects.filter(role='alumni', compte_active=True).count()
    nb_posts = Post.objects.filter(status=1).count()
    nb_etudiants = Profile.objects.filter(role='etudiant', compte_active=True).count()
    return render(request, "blog/dashboard_etudiant.html", {
        "user": request.user,
        "profile": profile,
        "feed": feed,
        "nb_notifications": nb_notifications,
        "nb_offres": nb_offres,
        "nb_alumni": nb_alumni,
        "nb_posts": nb_posts,
        "nb_etudiants": nb_etudiants,
        "nom_affiche": request.user.get_full_name() or request.user.username,
    })

@login_required
def dashboard_alumni(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = None
    nb_notifications = Notification.objects.filter(destinataire=request.user, lue=False).count()
    return render(request, "blog/dashboard_alumni.html", {
        "user": request.user,
        "profile": profile,
        "nom_affiche": request.user.get_full_name() or request.user.username,
        "nb_notifications": nb_notifications,
    })

@login_required
def profil_etudiant(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user, role='etudiant', compte_active=True)
    success = False
    if request.method == "POST":
        request.user.first_name = request.POST.get("prenom", request.user.first_name)
        request.user.last_name = request.POST.get("nom", request.user.last_name)
        request.user.email = request.POST.get("email", request.user.email)
        request.user.save()
        profile.annee_actuelle = request.POST.get("annee_actuelle", profile.annee_actuelle)
        profile.filiere = request.POST.get("filiere", profile.filiere)
        if request.FILES.get("photo"):
            profile.photo = request.FILES["photo"]
        profile.save()
        success = True
        nom = request.user.get_full_name() or request.user.username
        for admin_user in User.objects.filter(is_staff=True):
            Notification.objects.create(destinataire=admin_user, message=f"{nom} a mis à jour son profil.")
    return render(request, "blog/profil_etudiant.html", {"profile": profile, "user": request.user, "success": success})

@login_required
def profil_alumni(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user, role='alumni', compte_active=True)
    success = False
    if request.method == "POST":
        request.user.first_name = request.POST.get("prenom", request.user.first_name)
        request.user.last_name = request.POST.get("nom", request.user.last_name)
        request.user.email = request.POST.get("email", request.user.email)
        request.user.save()
        profile.filiere_alumni = request.POST.get("filiere_alumni", profile.filiere_alumni)
        profile.annee_licence = request.POST.get("annee_licence", profile.annee_licence)
        profile.en_poste = request.POST.get("en_poste") == "True"
        if request.FILES.get("photo"):
            profile.photo = request.FILES["photo"]
        profile.save()
        success = True
        nom = request.user.get_full_name() or request.user.username
        for admin_user in User.objects.filter(is_staff=True):
            Notification.objects.create(destinataire=admin_user, message=f"{nom} (alumni) a mis à jour son profil.")
    return render(request, "blog/profil_alumni.html", {"profile": profile, "user": request.user, "success": success})

@login_required
def offre_create(request):
    from .models import Offre
    success = False
    if request.method == "POST":
        titre = request.POST.get("titre", "").strip()
        entreprise = request.POST.get("entreprise", "").strip()
        ville = request.POST.get("ville", "Djibouti").strip()
        description = request.POST.get("description", "").strip()
        type_offre = request.POST.get("type_offre", "stage")
        niveau_requis = request.POST.get("niveau_requis", "tout")
        date_limite = request.POST.get("date_limite") or None
        if titre and entreprise and description:
            offre = Offre.objects.create(
                auteur=request.user,
                titre=titre,
                entreprise=entreprise,
                ville=ville,
                description=description,
                type_offre=type_offre,
                niveau_requis=niveau_requis,
                date_limite=date_limite,
                status=0,
            )
            for admin_user in User.objects.filter(is_staff=True):
                Notification.objects.create(
                    destinataire=admin_user,
                    message=f"Nouvelle offre en attente de validation de {request.user.get_full_name() or request.user.username} : {titre} chez {entreprise}"
                )
            success = True
    return render(request, "blog/offre_create.html", {"success": success})

@login_required
def mes_offres(request):
    from .models import Offre
    offres = Offre.objects.filter(auteur=request.user).order_by("-date_creation")
    return render(request, "blog/mes_offres.html", {"offres": offres})

@login_required
def mes_posts(request):
    posts = Post.objects.filter(auteur=request.user).order_by("-date_creation")
    return render(request, "blog/mes_posts.html", {"posts": posts})

@login_required
def favoris(request):
    from .models import FavoriOffre
    mes_favoris_posts = Favori.objects.filter(user=request.user).select_related('post__auteur__profile').order_by('-id')
    mes_favoris_offres = FavoriOffre.objects.filter(user=request.user).select_related('offre__auteur__profile').order_by('-id')
    nb_notifications = Notification.objects.filter(destinataire=request.user, lue=False).count()
    return render(request, "blog/favoris.html", {
        "mes_favoris_posts": mes_favoris_posts,
        "mes_favoris_offres": mes_favoris_offres,
        "nb_notifications": nb_notifications,
        "nb_favoris": mes_favoris_posts.count() + mes_favoris_offres.count(),
    })

@login_required
def offre_like(request, offre_id):
    from .models import Offre, LikeOffre
    offre = get_object_or_404(Offre, pk=offre_id)
    like, created = LikeOffre.objects.get_or_create(offre=offre, user=request.user)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
        if offre.auteur != request.user:
            Notification.objects.create(
                destinataire=offre.auteur,
                message=f"{request.user.get_full_name() or request.user.username} a aimé votre offre : {offre.titre}"
            )
            Notification.objects.create(
                destinataire=request.user,
                message=f"Vous avez aimé l'offre de {offre.auteur.get_full_name() or offre.auteur.username} : {offre.titre}"
            )
    return JsonResponse({'liked': liked, 'total': offre.likes.count()})

@login_required
def offre_favori(request, offre_id):
    from .models import Offre, FavoriOffre
    offre = get_object_or_404(Offre, pk=offre_id)
    favori, created = FavoriOffre.objects.get_or_create(offre=offre, user=request.user)
    if not created:
        favori.delete()
        en_favori = False
    else:
        en_favori = True
        Notification.objects.create(
            destinataire=request.user,
            message=f"Vous avez ajouté aux favoris l'offre : {offre.titre}"
        )
    return JsonResponse({'favoris': en_favori, 'total': offre.favoris.count()})

@login_required
def offre_stats(request, offre_id):
    from .models import Offre
    offre = get_object_or_404(Offre, pk=offre_id)
    likers = offre.likes.select_related('user').order_by('-id')[:3]
    return JsonResponse({
        'nb_likes': offre.likes.count(),
        'nb_favoris': offre.favoris.count(),
        'likers': [l.user.get_full_name() or l.user.username for l in likers],
    })

@login_required
def fil_alumni(request):
    from .models import Offre, CommentOffre
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = None
    posts = Post.objects.filter(status=1).order_by("-date_creation")
    offres_qs = Offre.objects.filter(status=1).order_by("-date_creation")
    posts_data = []
    for post in posts:
        posts_data.append({
            'type': 'post',
            'obj': post,
            'auteur': post.auteur,
            'date': post.date_creation,
            'liked': post.likes.filter(user=request.user).exists(),
            'en_favori': post.favoris.filter(user=request.user).exists(),
            'nb_likes': post.likes.count(),
            'nb_favoris': post.favoris.count(),
            'nb_comments': post.comments.filter(actif=True).count(),
            'comments': post.comments.filter(actif=True),
        })
    offres_data = []
    for offre in offres_qs:
        offres_data.append({
            'type': 'offre',
            'obj': offre,
            'auteur': offre.auteur,
            'date': offre.date_creation,
            'nb_likes_offre': offre.likes.count(),
            'nb_favoris_offre': offre.favoris.count(),
            'liked_offre': offre.likes.filter(user=request.user).exists(),
            'en_favori_offre': offre.favoris.filter(user=request.user).exists(),
            'comments_offre': CommentOffre.objects.filter(offre=offre, actif=True),
            'nb_comments_offre': CommentOffre.objects.filter(offre=offre, actif=True).count(),
        })
    feed = sorted(posts_data + offres_data, key=lambda x: x['date'], reverse=True)
    nb_notifications = Notification.objects.filter(destinataire=request.user, lue=False).count()
    return render(request, "blog/fil_alumni.html", {
        "user": request.user,
        "profile": profile,
        "feed": feed,
        "nb_notifications": nb_notifications,
        "nom_affiche": request.user.get_full_name() or request.user.username,
    })

@login_required
def fil_etudiant(request):
    from .models import Offre, CommentOffre
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = None
    posts = Post.objects.filter(status=1).order_by("-date_creation")
    offres_qs = Offre.objects.filter(status=1).order_by("-date_creation")
    posts_data = []
    for post in posts:
        posts_data.append({
            'type': 'post',
            'obj': post,
            'auteur': post.auteur,
            'date': post.date_creation,
            'liked': post.likes.filter(user=request.user).exists(),
            'en_favori': post.favoris.filter(user=request.user).exists(),
            'nb_likes': post.likes.count(),
            'nb_favoris': post.favoris.count(),
            'nb_comments': post.comments.filter(actif=True).count(),
            'comments': post.comments.filter(actif=True),
        })
    offres_data = []
    for offre in offres_qs:
        offres_data.append({
            'type': 'offre',
            'obj': offre,
            'auteur': offre.auteur,
            'date': offre.date_creation,
            'nb_likes_offre': offre.likes.count(),
            'nb_favoris_offre': offre.favoris.count(),
            'liked_offre': offre.likes.filter(user=request.user).exists(),
            'en_favori_offre': offre.favoris.filter(user=request.user).exists(),
            'comments_offre': CommentOffre.objects.filter(offre=offre, actif=True),
            'nb_comments_offre': CommentOffre.objects.filter(offre=offre, actif=True).count(),
        })
    feed = sorted(posts_data + offres_data, key=lambda x: x['date'], reverse=True)
    nb_notifications = Notification.objects.filter(destinataire=request.user, lue=False).count()
    return render(request, "blog/fil_etudiant.html", {
        "user": request.user,
        "profile": profile,
        "feed": feed,
        "nb_notifications": nb_notifications,
    })

@login_required
def posts_etudiant(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = None
    posts = Post.objects.filter(status=1).order_by("-date_creation")
    posts_data = []
    for post in posts:
        posts_data.append({
            'type': 'post',
            'obj': post,
            'auteur': post.auteur,
            'date': post.date_creation,
            'liked': post.likes.filter(user=request.user).exists(),
            'en_favori': post.favoris.filter(user=request.user).exists(),
            'nb_likes': post.likes.count(),
            'nb_favoris': post.favoris.count(),
            'nb_comments': post.comments.filter(actif=True).count(),
            'comments': post.comments.filter(actif=True),
        })
    nb_notifications = Notification.objects.filter(destinataire=request.user, lue=False).count()
    return render(request, "blog/posts_etudiant.html", {
        "user": request.user,
        "profile": profile,
        "feed": posts_data,
        "nb_notifications": nb_notifications,
        "nom_affiche": request.user.get_full_name() or request.user.username,
    })

@login_required
def comment_supprimer(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if comment.auteur == request.user:
        comment.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})
# ============================================================
# Colle ces deux fonctions dans ton views.py
# après ta fonction offre_commenter existante
# ============================================================

@login_required
def offre_commenter(request, offre_id):
    from .models import CommentOffre, Offre
    offre = get_object_or_404(Offre, pk=offre_id)
    if request.method == "POST":
        contenu = request.POST.get("contenu", "").strip()
        if contenu:
            comment = CommentOffre.objects.create(
                offre=offre, auteur=request.user, contenu=contenu, actif=True
            )
            if offre.auteur != request.user:
                Notification.objects.create(
                    destinataire=offre.auteur,
                    message=f"{request.user.get_full_name() or request.user.username} a commenté votre offre : {offre.titre}"
                )
            return JsonResponse({
                'success': True,
                'id': comment.id,
                'auteur': request.user.get_full_name() or request.user.username,
                'contenu': comment.contenu,
                'date': comment.date_creation.strftime("%d/%m %H:%M"),
                'mine': True,
            })
    return JsonResponse({'success': False})


@login_required
def offre_comment_supprimer(request, comment_id):
    from .models import CommentOffre
    comment = get_object_or_404(CommentOffre, pk=comment_id)
    if comment.auteur == request.user:
        comment.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Non autorisé'}, status=403)
@login_required
def changer_mot_de_passe(request):
    if request.method == "POST":
        ancien = request.POST.get("ancien_mdp", "")
        nouveau = request.POST.get("nouveau_mdp", "")
        confirm = request.POST.get("confirm_mdp", "")
        if not request.user.check_password(ancien):
            return render(request, "blog/profil_etudiant.html", {
                "profile": request.user.profile,
                "pwd_error": "Mot de passe actuel incorrect."
            })
        if nouveau != confirm:
            return render(request, "blog/profil_etudiant.html", {
                "profile": request.user.profile,
                "pwd_error": "Les deux mots de passe ne correspondent pas."
            })
        if len(nouveau) < 8:
            return render(request, "blog/profil_etudiant.html", {
                "profile": request.user.profile,
                "pwd_error": "Le mot de passe doit faire au moins 8 caractères."
            })
        request.user.set_password(nouveau)
        request.user.save()
        update_session_auth_hash(request, request.user)
        return render(request, "blog/profil_etudiant.html", {
            "profile": request.user.profile,
            "pwd_success": True
        })
    return redirect("profil_etudiant")

@login_required
def changer_mot_de_passe_alumni(request):
    if request.method == "POST":
        ancien = request.POST.get("ancien_mdp", "")
        nouveau = request.POST.get("nouveau_mdp", "")
        confirm = request.POST.get("confirm_mdp", "")
        if not request.user.check_password(ancien):
            return render(request, "blog/profil_alumni.html", {
                "profile": request.user.profile,
                "pwd_error": "Mot de passe actuel incorrect."
            })
        if nouveau != confirm:
            return render(request, "blog/profil_alumni.html", {
                "profile": request.user.profile,
                "pwd_error": "Les deux mots de passe ne correspondent pas."
            })
        if len(nouveau) < 8:
            return render(request, "blog/profil_alumni.html", {
                "profile": request.user.profile,
                "pwd_error": "Le mot de passe doit faire au moins 8 caractères."
            })
        request.user.set_password(nouveau)
        request.user.save()
        update_session_auth_hash(request, request.user)
        return render(request, "blog/profil_alumni.html", {
            "profile": request.user.profile,
            "pwd_success": True
        })
    return redirect("profil_alumni")