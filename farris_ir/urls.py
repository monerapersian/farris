"""
URL configuration for farris_ir project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from django.urls import path, re_path, include
from django.views.static import serve
from django.contrib.sitemaps.views import sitemap
from website.sitemaps import StaticViewSitemap, CategorySitemap, ProductSitemap, ArticleSitemap
from .sitemap import (
    SafeStaticViewSitemap,
    SafeCategorySitemap,
    SafeProductSitemap,
    SafeArticleSitemap,
)

sitemaps = {
    "static": SafeStaticViewSitemap,
    "categories": SafeCategorySitemap,
    "products": SafeProductSitemap,
    "articles": SafeArticleSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('website.urls')),

    # main index sitemap
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django_sitemap"),

    # sub-sitemaps
    # path('sitemap-pages.xml', sitemap, {'sitemaps': {"pages": StaticViewSitemap}}, name='sitemap-pages'),
    # path('sitemap-categories.xml', sitemap, {'sitemaps': {"categories": CategorySitemap}}, name='sitemap-categories'),
    # path('sitemap-products.xml', sitemap, {'sitemaps': {"products": ProductSitemap}}, name='sitemap-products'),
    # path('sitemap-articles.xml', sitemap, {'sitemaps': {"articles": ArticleSitemap}}, name='sitemap-articles'),
]

if not settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]

# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

