from django.urls import path, include
from django.contrib import admin
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.api.urls')),
    path('api/patent/', include('apps.patent.urls')),
    path('api/auth/', include('apps.accounts.urls')),
    path('billing/', include('apps.billing.urls')),
    path('health/', TemplateView.as_view(template_name='health.html', content_type='text/html'), name='health'),
]
