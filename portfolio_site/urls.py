from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from portfolio import views as portfolio_views
from portfolio.sitemaps import PortfolioSitemap, StaticViewSitemap


sitemaps = {
    'static': StaticViewSitemap,
    'portfolio': PortfolioSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('sitemap-images.xml', portfolio_views.sitemap_images, name='sitemap_images'),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('robots.txt', portfolio_views.robots_txt, name='robots_txt'),
    path('', include('portfolio.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
