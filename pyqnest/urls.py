from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from papers import views as papers_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls')),
    path('robots.txt', papers_views.robots_txt, name="robots_txt"),
    path('sitemap.xml', papers_views.sitemap_xml, name="sitemap"),
    path('', include('papers.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
