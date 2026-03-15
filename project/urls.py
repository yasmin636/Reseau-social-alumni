from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views as project_views

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', project_views.home, name='home'),
    path('', include('blog.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)