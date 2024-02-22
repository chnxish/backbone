"""backbone URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

api = [
    path("accounts/", include("accounts.urls.api_urls"), name="api-accounts"),
    path("friendship/", include("friendship.urls.api_urls"), name="api-friendship"),
    path("chat/", include("chat.urls.api_urls"), name="api-chat"),
    path("note/", include("note.urls.api_urls"), name="api-note"),
    path("todo/", include("todo.urls.api_urls"), name="api-todo"),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api)),
    path("", include("accounts.urls.view_urls"), name="accounts"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
