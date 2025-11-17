from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Product, Category, Article

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "monthly"

    def items(self):
        return ["home", "products_list", "articles_list", "tutorial", "call_us"]

    def location(self, item):
        return reverse(item)


class CategorySitemap(Sitemap):
    priority = 0.7
    changefreq = "weekly"

    def items(self):
        return Category.objects.all()


class ProductSitemap(Sitemap):
    priority = 1.0
    changefreq = "weekly"

    def items(self):
        return Product.objects.all()


class ArticleSitemap(Sitemap):
    priority = 0.6
    changefreq = "weekly"

    def items(self):
        return Article.objects.all()