from django import forms
from django.contrib.auth.models import User
from .models import Comment, Post, Profile, Offre

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["contenu"]

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["titre", "contenu", "photo"]
        widgets = {
            'titre': forms.TextInput(attrs={'placeholder': 'Titre (optionnel)', 'class': 'form-input'}),
            'contenu': forms.Textarea(attrs={'placeholder': 'Quoi de neuf ? Partagez votre expérience...', 'class': 'form-input', 'rows': 5}),
        }

# ===============================
# FORMULAIRE OFFRE (NOUVEAU)
# ===============================
class OffreForm(forms.ModelForm):
    class Meta:
        model = Offre
        fields = ['type_offre', 'titre', 'entreprise', 'ville', 'description', 'niveau_requis', 'date_limite']
        widgets = {
            'type_offre': forms.Select(attrs={'class': 'form-input'}),
            'titre': forms.TextInput(attrs={'placeholder': 'Ex: Développeur Web Junior', 'class': 'form-input'}),
            'entreprise': forms.TextInput(attrs={'placeholder': "Nom de l'entreprise", 'class': 'form-input'}),
            'ville': forms.TextInput(attrs={'placeholder': 'Ex: Djibouti', 'class': 'form-input'}),
            'description': forms.Textarea(attrs={'placeholder': 'Description du poste, missions, compétences requises...', 'class': 'form-input', 'rows': 6}),
            'niveau_requis': forms.Select(attrs={'class': 'form-input'}),
            'date_limite': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
        }
        labels = {
            'type_offre': "Type d'offre",
            'titre': 'Intitulé du poste',
            'entreprise': 'Entreprise',
            'ville': 'Ville',
            'description': 'Description',
            'niveau_requis': "Niveau d'études requis",
            'date_limite': 'Date limite de candidature',
        }

# ===============================
# FORMULAIRE INSCRIPTION ÉTUDIANT
# ===============================
class RegisterForm(forms.Form):

    nom = forms.CharField(max_length=50, label="Nom",
        widget=forms.TextInput(attrs={'placeholder': 'Votre nom', 'class': 'form-input'}))
    prenom = forms.CharField(max_length=50, label="Prénom",
        widget=forms.TextInput(attrs={'placeholder': 'Votre prénom', 'class': 'form-input'}))
    username = forms.CharField(max_length=50, label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={'placeholder': "Nom d'utilisateur", 'class': 'form-input'}))
    email = forms.EmailField(label="Email",
        widget=forms.EmailInput(attrs={'placeholder': 'votre@email.com', 'class': 'form-input'}))
    annee_actuelle = forms.CharField(max_length=20, label="Année actuelle",
        widget=forms.TextInput(attrs={'placeholder': 'Ex: L1, L2, L3, M1, M2', 'class': 'form-input'}))
    filiere = forms.CharField(max_length=100, label="Filière",
        widget=forms.TextInput(attrs={'placeholder': 'Ex: Informatique, Génie Civil...', 'class': 'form-input'}))
    password = forms.CharField(label="Mot de passe",
        widget=forms.PasswordInput(attrs={'placeholder': 'Mot de passe', 'class': 'form-input'}))
    password_confirm = forms.CharField(label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={'placeholder': 'Répéter le mot de passe', 'class': 'form-input'}))

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur est déjà pris.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data


# ===============================
# FORMULAIRE INSCRIPTION ALUMNI
# ===============================
class RegisterAlumniForm(forms.Form):

    nom = forms.CharField(max_length=50, label="Nom",
        widget=forms.TextInput(attrs={'placeholder': 'Votre nom', 'class': 'form-input'}))
    prenom = forms.CharField(max_length=50, label="Prénom",
        widget=forms.TextInput(attrs={'placeholder': 'Votre prénom', 'class': 'form-input'}))
    username = forms.CharField(max_length=50, label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={'placeholder': "Nom d'utilisateur", 'class': 'form-input'}))
    email = forms.EmailField(label="Email",
        widget=forms.EmailInput(attrs={'placeholder': 'votre@email.com', 'class': 'form-input'}))
    annee_licence = forms.CharField(max_length=10, label="Année de licence",
        widget=forms.TextInput(attrs={'placeholder': 'Ex: 2021', 'class': 'form-input'}))
    filiere_alumni = forms.CharField(max_length=100, label="Filière étudiée",
        widget=forms.TextInput(attrs={'placeholder': 'Ex: Informatique...', 'class': 'form-input'}))
    en_poste = forms.BooleanField(required=False, label="Je travaille actuellement")
    password = forms.CharField(label="Mot de passe",
        widget=forms.PasswordInput(attrs={'placeholder': 'Mot de passe', 'class': 'form-input'}))
    password_confirm = forms.CharField(label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={'placeholder': 'Répéter le mot de passe', 'class': 'form-input'}))

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur est déjà pris.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password_confirm')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data