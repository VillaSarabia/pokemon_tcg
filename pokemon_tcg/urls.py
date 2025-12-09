from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Your custom app URLs first
    path('', include('core.urls')),
    
    # Then Django admin with its own namespace
    path('django-admin/', admin.site.urls),  # Changed from 'admin/' to 'django-admin/'
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom admin site title
admin.site.site_header = "Pokemon TCG - Administración"
admin.site.site_title = "Pokemon TCG Admin"
admin.site.index_title = "Bienvenido al Panel de Administración"