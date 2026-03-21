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

    auteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    titre = models.CharField(max_length=200, blank=True, null=True)
    contenu = models.TextField()
    photo = models.ImageField(upload_to='posts/', blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS, default=0)

    class Meta:
        ordering = ["-date_creation"]

    def __str__(self):
        return self.titre or f"Post de {self.auteur.username}"


# ===============================
# MODELE COMMENTAIRE
# ===============================
class Comment(models.Model):

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
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
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='etudiant')
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    annee_actuelle = models.CharField(max_length=20, blank=True, null=True)
    filiere = models.CharField(max_length=100, blank=True, null=True)
    compte_active = models.BooleanField(default=False)
    annee_licence = models.CharField(max_length=10, blank=True, null=True)
    filiere_alumni = models.CharField(max_length=100, blank=True, null=True)
    en_poste = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


# ===============================
# MODELE NOTIFICATION
# ===============================
class Notification(models.Model):

    destinataire = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
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

    expediteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages_envoyes")
    destinataire = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages_recus")
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

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.user.username} like {self.post.titre}"


# ===============================
# MODELE FAVORI
# ===============================
class Favori(models.Model):

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="favoris")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favoris")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.user.username} favori {self.post.titre}"


# ===============================
# MODELE OFFRE
# ===============================
class Offre(models.Model):

    TYPE_CHOICES = (
        ('stage', 'Stage'),
        ('emploi', 'Emploi'),
        ('cdi', 'CDI'),
        ('cdd', 'CDD'),
        ('alternance', 'Alternance'),
        ('freelance', 'Freelance'),
    )

    NIVEAU_CHOICES = (
        ('tout', 'Tous niveaux'),
        ('licence', 'Licence (L1-L3)'),
        ('master', 'Master (M1-M2)'),
        ('doctorat', 'Doctorat'),
        ('bac', 'Bac'),
    )

    auteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name="offres")
    type_offre = models.CharField(max_length=20, choices=TYPE_CHOICES, default='stage')
    titre = models.CharField(max_length=200)
    entreprise = models.CharField(max_length=200)
    ville = models.CharField(max_length=100, default='Djibouti')
    description = models.TextField()
    niveau_requis = models.CharField(max_length=20, choices=NIVEAU_CHOICES, default='tout')
    date_limite = models.DateField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    # Contact
    email_contact = models.EmailField(blank=True, null=True)
    telephone_contact = models.CharField(max_length=20, blank=True, null=True)

    # Champs STAGE
    duree_stage = models.CharField(max_length=50, blank=True, null=True, help_text="Ex: 3 mois, 6 mois")
    indemnite = models.CharField(max_length=100, blank=True, null=True, help_text="Ex: 50 000 DJF/mois")

    # Champs EMPLOI / CDI / CDD
    salaire = models.CharField(max_length=100, blank=True, null=True, help_text="Ex: 150 000 DJF/mois")
    experience_requise = models.CharField(max_length=100, blank=True, null=True, help_text="Ex: 2 ans minimum")

    # Champs ALTERNANCE
    ecole_partenaire = models.CharField(max_length=200, blank=True, null=True)

    # Champs FREELANCE
    budget = models.CharField(max_length=100, blank=True, null=True, help_text="Ex: 500 000 DJF")
    delai = models.CharField(max_length=100, blank=True, null=True, help_text="Ex: 2 semaines")

    class Meta:
        ordering = ["-date_creation"]

    def __str__(self):
        return f"{self.titre} — {self.entreprise}"
    # ===============================
# MODELE LIKE OFFRE
# ===============================
class LikeOffre(models.Model):

    offre = models.ForeignKey(Offre, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes_offres")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('offre', 'user')

    def __str__(self):
        return f"{self.user.username} like {self.offre.titre}"


# ===============================
# MODELE FAVORI OFFRE
# ===============================
class FavoriOffre(models.Model):

    offre = models.ForeignKey(Offre, on_delete=models.CASCADE, related_name="favoris")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favoris_offres")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('offre', 'user')

    def __str__(self):
        return f"{self.user.username} favori {self.offre.titre}"