from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from .models import Post, Comment, Profile
from .forms import CommentForm, PostForm

# ===============================
# LISTE DES POSTS (PAGE ACCUEIL)
# ===============================

class PostList(generic.ListView):
    queryset = Post.objects.filter(status=1).order_by("-date_creation")
    template_name = "index.html"


# ===============================
# DASHBOARD GENERAL
# ===============================

class DashboardView(generic.ListView):
    model = Post
    template_name = "blog/dashboard.html"
    context_object_name = "post_list"


# ===============================
# DETAIL POST
# ===============================

def post_detail(request, slug):

    template_name = "post_detail.html"

    post = get_object_or_404(Post, slug=slug)

    comments = post.comments.filter(active=True)

    new_comment = None

    if request.method == "POST":

        comment_form = CommentForm(data=request.POST)

        if comment_form.is_valid():

            new_comment = comment_form.save(commit=False)

            new_comment.post = post

            new_comment.save()

    else:
        comment_form = CommentForm()

    return render(
        request,
        template_name,
        {
            "post": post,
            "comments": comments,
            "new_comment": new_comment,
            "comment_form": comment_form,
        },
    )


# ===============================
# CREER UN POST
# ===============================

@login_required
def post_create(request):

    if request.method == "POST":

        form = PostForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect('dashboard')

    else:
        form = PostForm()

    return render(request, 'blog/post_create.html', {'form': form})


# ===============================
# OFFRES
# ===============================

@login_required
def offres(request):
    return render(request, "blog/offres.html")


# ===============================
# FAVORIS
# ===============================

@login_required
def favoris(request):
    return render(request, "blog/favoris.html")


# ===============================
# NOTIFICATIONS
# ===============================

@login_required
def notifications(request):
    return render(request, "blog/notifications.html")


# ===============================
# INSCRIPTION
# ===============================

def register(request):

    if request.method == "POST":

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        # vérifier si utilisateur existe
        if User.objects.filter(username=username).exists():

            return render(
                request,
                "register.html",
                {"error": "Utilisateur déjà existant"}
            )

        # créer utilisateur
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return redirect("login")

    return render(request, "register.html")


# ===============================
# CONNEXION
# ===============================

def login_view(request):

    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            # On récupère (ou crée) le profil associé à l'utilisateur
            profile, created = Profile.objects.get_or_create(
                user=user,
                defaults={"role": "etudiant"}  # rôle par défaut si aucun profil
            )

            # redirection selon le rôle
            if profile.role == "etudiant":
                return redirect("dashboard_etudiant")

            if profile.role == "alumni":
                return redirect("dashboard_alumni")

            return redirect("dashboard")

        else:

            return render(
                request,
                "login.html",
                {"error": "Utilisateur ou mot de passe incorrect"}
            )

    return render(request, "login.html")

# ===============================
# DASHBOARD ETUDIANT
# ===============================

@login_required
def dashboard_etudiant(request):
    # charger les offres, etc.
    return render(request, "blog/dashboard_etudiant.html", {"offres": offres})


# ===============================
# DASHBOARD ALUMNI
# ===============================

@login_required
def dashboard_alumni(request):

    return render(request, "blog/dashboard_alumni.html")