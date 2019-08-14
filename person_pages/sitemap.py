"""
Sitemap for person pages app.
"""
from django.contrib.sitemaps import GenericSitemap

from .models import PersonPage

PersonPage_Sitemap = GenericSitemap({"queryset": PersonPage.objects.active()})
