from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Project


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return ['home']

    def location(self, item):
        return reverse(item)


class PortfolioSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Project.objects.all()

    def lastmod(self, obj):
        return obj.created_at