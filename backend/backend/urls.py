from django.contrib import admin
from django.urls import path, include

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("test/", include('authentication.urls')),
    path('posts/', include('posts.urls')),
]
