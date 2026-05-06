import importlib.util

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from portfolio import views as portfolio_views
from portfolio.sitemaps import PortfolioSitemap, StaticViewSitemap


sitemaps = {
    'static': StaticViewSitemap,
    'portfolio': PortfolioSitemap,
}


urlpatterns = [
    # Vrai back-office Django avec URL d'acces non publique.
    path(settings.ADMIN_URL, admin.site.urls),

    # Routes techniques et SEO.
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('sitemap-images.xml', portfolio_views.sitemap_images, name='sitemap_images'),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('robots.txt', portfolio_views.robots_txt, name='robots_txt'),
    path('csp-report/', portfolio_views.csp_report, name='csp_report'),

    # Routes publiques du site.
    path('', include('portfolio.urls')),
]


# Pages d'erreur personnalisees.
handler400 = 'portfolio.views.bad_request'
handler403 = 'portfolio.views.permission_denied'
handler404 = 'portfolio.views.page_not_found'
handler500 = 'portfolio.views.server_error'


# HoneyGuard ajoute des routes pieges si le package est installe.
if importlib.util.find_spec('django_honeyguard') is not None:
    from django_honeyguard.views import FakeDjangoAdminView, FakeWPAdminView

    honeyguard_urlpatterns = [
        # Faux points d'entree souvent testes par les bots.
        path('admin/', FakeWPAdminView.as_view(), name='fake_admin'),
        path('login.php', FakeWPAdminView.as_view(), name='fake_php_login'),
        path('django-admin/', FakeDjangoAdminView.as_view(), name='fake_django_admin'),

        # Routes pieges additionnelles fournies par le package.
        path('security/', include('django_honeyguard.urls')),
    ]

    urlpatterns = honeyguard_urlpatterns + urlpatterns


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
