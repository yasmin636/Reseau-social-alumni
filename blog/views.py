from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
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

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_staff or user.is_superuser:
                return render(request, "login.html", {"error": "Utilisez la page de connexion administrateur."})
            try:
                profile = user.profile
            except Profile.DoesNotExist:
                profile = Profile.objects.create(user=user, role='etudiant', compte_active=False)
            if not profile.compte_active:
                return render(request, "login.html", {"error": "pending"})
            login(request, user)
            if profile.role == "etudiant":
                return redirect("dashboard_etudiant")
            elif profile.role == "alumni":
                return redirect("dashboard_alumni")
            return redirect("dashboard")
        else:
            return render(request, "login.html", {"error": "Nom d'utilisateur ou mot de passe incorrect."})
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
    users = User.objects.select_related("profile").all().order_by("date_joined")
    pending_posts = Post.objects.filter(status=0).select_related("auteur").order_by("-date_creation")
    pending_users = []
    for u in users:
        try:
            if not u.profile.compte_active and not u.is_staff:
                pending_users.append(u)
        except Profile.DoesNotExist:
            pass
    return render(request, "admin.html", {"users": users, "pending_posts": pending_posts, "last_messages": [], "pending_users": pending_users})

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
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.auteur = request.user
            post.save()
            etudiants = User.objects.filter(profile__role='etudiant', profile__compte_active=True)
            for etudiant in etudiants:
                Notification.objects.create(destinataire=etudiant,
                    message=f"Nouveau post : {post.titre} — par {request.user.get_full_name() or request.user.username}")
            return redirect('dashboard')
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
        # Notifier l'auteur du post
        if post.auteur != request.user:
            Notification.objects.create(
                destinataire=post.auteur,
                message=f"{request.user.get_full_name() or request.user.username} a aimé votre post : {post.titre}"
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
    return JsonResponse({'favoris': en_favori, 'total': post.favoris.count()})

@login_required
def post_commenter(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == "POST":
        contenu = request.POST.get("contenu", "").strip()
        if contenu:
            comment = Comment.objects.create(post=post, auteur=request.user, contenu=contenu, actif=True)
            # Notifier l'auteur du post
            if post.auteur != request.user:
                Notification.objects.create(
                    destinataire=post.auteur,
                    message=f"{request.user.get_full_name() or request.user.username} a commenté votre post : {post.titre}"
                )
            return JsonResponse({
                'success': True,
                'auteur': request.user.get_full_name() or request.user.username,
                'contenu': comment.contenu,
                'date': comment.date_creation.strftime("%d/%m/%Y à %H:%M")
            })
    return JsonResponse({'success': False})

@login_required
def chat_page(request, user_id=None):
    messages_envoyes = Message.objects.filter(expediteur=request.user).values_list('destinataire', flat=True)
    messages_recus = Message.objects.filter(destinataire=request.user).values_list('expediteur', flat=True)
    contact_ids = set(list(messages_envoyes) + list(messages_recus))
    contacts = User.objects.filter(id__in=contact_ids)
    selected_user = None
    conversation = []
    if user_id:
        selected_user = get_object_or_404(User, pk=user_id)
        conversation = Message.objects.filter(
            Q(expediteur=request.user, destinataire=selected_user) |
            Q(expediteur=selected_user, destinataire=request.user)
        ).order_by("date_envoi")
        conversation.filter(destinataire=request.user, lu=False).update(lu=True)
        # Notifier l'alumni qu'un étudiant veut le contacter (première fois seulement)
        if not Message.objects.filter(expediteur=request.user, destinataire=selected_user).exists():
            nom = request.user.get_full_name() or request.user.username
            Notification.objects.create(
                destinataire=selected_user,
                message=f"{nom} veut vous contacter via le chat."
            )
    tous_alumni = User.objects.filter(profile__role='alumni', profile__compte_active=True)
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
            # Notifier le destinataire
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
    return render(request, "blog/offres.html")

@login_required
def favoris(request):
    mes_favoris = Favori.objects.filter(user=request.user).select_related('post')
    return render(request, "blog/favoris.html", {"mes_favoris": mes_favoris})

@login_required
def notifications(request):
    notifs = Notification.objects.filter(destinataire=request.user).order_by("-date_creation")
    notifs.update(lue=True)
    return render(request, "notifications.html", {"notifs": notifs})

@login_required
def dashboard_etudiant(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = None
    posts = Post.objects.filter(status=1).order_by("-date_creation")
    alumni_list = User.objects.filter(profile__role='alumni', profile__compte_active=True)
    posts_data = []
    for post in posts:
        posts_data.append({
            'post': post,
            'liked': post.likes.filter(user=request.user).exists(),
            'en_favori': post.favoris.filter(user=request.user).exists(),
            'nb_likes': post.likes.count(),
            'nb_favoris': post.favoris.count(),
            'nb_comments': post.comments.filter(actif=True).count(),
            'comments': post.comments.filter(actif=True),
        })
    return render(request, "blog/dashboard_etudiant.html", {
        "user": request.user,
        "profile": profile,
        "posts_data": posts_data,
        "alumni_list": alumni_list,
        "nom_affiche": request.user.get_full_name() or request.user.username,
    })

@login_required
def dashboard_alumni(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = None
    return render(request, "blog/dashboard_alumni.html", {
        "user": request.user,
        "profile": profile,
        "nom_affiche": request.user.get_full_name() or request.user.username,
    })

# ===============================
# PROFIL ÉTUDIANT
# ===============================
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

# ===============================
# PROFIL ALUMNI (AJOUTÉ)
# ===============================
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