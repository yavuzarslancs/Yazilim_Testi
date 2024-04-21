"""
URL configuration for yazilim_testi_proje project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, include
from django.contrib import admin
from app.views import home  # app'in views.py dosyasından home fonksiyonunu import edin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('app/', include('app.urls')),  # Bu zaten mevcutsa değiştirmeyin
    path('', home, name='home'),  # Kök URL için home görünümünü ekleyin
]

