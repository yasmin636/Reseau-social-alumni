from django.db import models
from django.contrib.auth.models import User


STATUS = ((0, "Draft"), (1, "Publish"))


class Post(models.Model):
    titre = models.CharField(max_length=200, blank=True)        # ✅ titre au lieu de title
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")  # ✅ auteur au lieu de author
    contenu = models.TextField()                                # ✅ contenu au lieu de content
    photo = models.ImageField(upload_to='posts/', blank=True, null=True)  # ✅ ajoute photo
    date_creation = models.DateTimeField(auto_now_add=True)     # ✅ date_creation au lieu de created_on
    updated_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(choices=STATUS, default=0)

    class Meta:
        ordering = ["-date_creation"]

    def __str__(self):
        return self.titre


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_on"]

    def __str__(self):
        return "Comment {} by {}".format(self.body, self.name)
