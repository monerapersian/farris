from django.contrib.sitemaps import Sitemap
from django.urls import reverse
import traceback

# ---------------------
# Safe Static Sitemap
# ---------------------
class SafeStaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "monthly"

    def items(self):
        return ["home", "products_list", "articles_list", "tutorial", "call_us"]

    def location(self, item):
        try:
            return reverse(item)
        except:
            return "/"  # جلوگیری از ارور 500


# ---------------------
# Safe Category Sitemap
# ---------------------
class SafeCategorySitemap(Sitemap):
    priority = 0.7
    changefreq = "weekly"

    def items(self):
        try:
            from .models import Category
            return Category.objects.all()
        except Exception as e:
            print("Category Sitemap Error:", e)
            print(traceback.format_exc())
            return []  # اگر DB مشکل داشت → خروجی خالی


# ---------------------
# Safe Product Sitemap
# ---------------------
class SafeProductSitemap(Sitemap):
    priority = 1.0
    changefreq = "weekly"

    def items(self):
        try:
            from .models import Product
            return Product.objects.all()
        except Exception as e:
            print("Product Sitemap Error:", e)
            print(traceback.format_exc())
            return []


# ---------------------
# Safe Article Sitemap
# ---------------------
class SafeArticleSitemap(Sitemap):
    priority = 0.6
    changefreq = "weekly"

    def items(self):
        try:
            from .models import Article
            return Article.objects.all()
        except Exception as e:
            print("Article Sitemap Error:", e)
            print(traceback.format_exc())
            return []