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

    auteur = models.ForeignKey(User, on_delete=models.CASCADE)
    contenu = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    actif = models.BooleanField(default=True)

    def __str__(self):
        return f"Commentaire de {self.auteur}"


# ===============================
# MODELE PROFILE
# ===============================
class Profile(models.Model):

    ROLE_CHOICES = (
        ('etudiant', 'Étudiant'),
        ('alumni', 'Alumni'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='etudiant'
    )

    photo = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True
    )

    annee_actuelle = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Ex: L1, L2, L3, M1, M2"
    )

    filiere = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Ex: Informatique, Génie Civil..."
    )

    compte_active = models.BooleanField(
        default=False,
        help_text="L'admin doit activer ce compte"
    )

    # Champs ALUMNI
    annee_licence = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="Année d'obtention de la licence (ex: 2021)"
    )

    filiere_alumni = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Filière étudiée"
    )

    en_poste = models.BooleanField(
        default=False,
        help_text="Est-ce que l'alumni travaille actuellement ?"
    )

    def __str__(self):
        return f"{self.user.username} ({self.role})"


# ===============================
# MODELE NOTIFICATION
# ===============================
class Notification(models.Model):

    destinataire = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    message = models.TextField()

    date_creation = models.DateTimeField(auto_now_add=True)

    lue = models.BooleanField(default=False)

    class Meta:
        ordering = ["-date_creation"]

    def __str__(self):
        return f"Notif pour {self.destinataire.username} — {self.message[:40]}"


# ===============================
# MODELE MESSAGE (Chat)
# ===============================
class Message(models.Model):

    expediteur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="messages_envoyes"
    )

    destinataire = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="messages_recus"
    )

    contenu = models.TextField()

    date_envoi = models.DateTimeField(auto_now_add=True)

    lu = models.BooleanField(default=False)

    class Meta:
        ordering = ["date_envoi"]

    def __str__(self):
        return f"{self.expediteur.username} → {self.destinataire.username}: {self.contenu[:30]}"


# ===============================
# MODELE LIKE
# ===============================
class Like(models.Model):

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="likes"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="likes"
    )

    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.user.username} like {self.post.titre}"


# ===============================
# MODELE FAVORI
# ===============================
class Favori(models.Model):

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="favoris"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favoris"
    )

    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.user.username} favori {self.post.titre}"