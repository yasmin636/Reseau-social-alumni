from django.contrib import admin
from .models import Post, Comment, Profile


class PostAdmin(admin.ModelAdmin):

    list_display = ('titre', 'auteur', 'date_creation', 'status')

    list_filter = ('status', 'date_creation')

    search_fields = ['titre', 'contenu']


class CommentAdmin(admin.ModelAdmin):

    list_display = ('auteur', 'contenu', 'date_creation', 'actif')

    list_filter = ('actif', 'date_creation')

    search_fields = ['contenu']


admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Profile)