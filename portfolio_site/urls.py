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
    path('robots.txt', portfolio_views.robots_txt, name='robots_txt'),
    path('', include('portfolio.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
