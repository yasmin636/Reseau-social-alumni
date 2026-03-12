from django.db import models
from django.contrib.auth.models import User


STATUS = (
    (0, "Brouillon"),
    (1, "Publié")
)


# ===============================
# MODELE POST (Publication)
# ===============================
class Post(models.Model):

    auteur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts"
    )

    titre = models.CharField(max_length=200)

    contenu = models.TextField()

    date_creation = models.DateTimeField(auto_now_add=True)

    status = models.IntegerField(choices=STATUS, default=1)

    class Meta:
        ordering = ["-date_creation"]

    def __str__(self):
        return self.titre


# ===============================
# MODELE COMMENTAIRE
# ===============================
class Comment(models.Model):

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    auteur = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    contenu = models.TextField()

    date_creation = models.DateTimeField(auto_now_add=True)

    actif = models.BooleanField(default=True)

    def __str__(self):
        return f"Commentaire de {self.auteur}"


# ===============================
# MODELE PROFILE (Role)
# ===============================
class Profile(models.Model):

    ROLE_CHOICES = (
        ('etudiant', 'Étudiant'),
        ('alumni', 'Alumni'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return self.user.username