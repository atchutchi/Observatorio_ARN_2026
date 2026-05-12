from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse


def health_check(_request):
    return JsonResponse({'status': 'ok'})

urlpatterns = [
    path('healthz/', health_check, name='health-check'),
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.api.v1.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
