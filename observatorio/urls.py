"""observatorio URL Configuration

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
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from home import views as home_views
from observatorio.health import health_check, health_check_detailed, readiness_check, liveness_check

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Health Check Endpoints
    path('health/', health_check, name='health_check'),
    path('health/detailed/', health_check_detailed, name='health_check_detailed'),
    path('health/ready/', readiness_check, name='readiness_check'),
    path('health/alive/', liveness_check, name='liveness_check'),
    
    # Authentication
    path('accounts/', include('allauth.urls')),  # URLs para autenticação
    path('accounts/profile/', home_views.profile, name='account_profile'),
    
    # Applications
    path('', include('home.urls')),  # URLs para a aplicação home
    path('questionarios/', include('questionarios.urls', namespace='questionarios')),  # URLs para a aplicação questionarios
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),  # URLs para a aplicação dashboard
]

# Adicionar URLs para servir arquivos estáticos e de mídia durante o desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
