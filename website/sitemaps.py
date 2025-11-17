from django.http import HttpResponse
from django.urls import reverse
from django.views.decorators.cache import cache_page
import traceback

CACHE_TIME = 60 * 30  # 30 دقیقه

@cache_page(CACHE_TIME)
def sitemap_safe(request):
    """
    نسخه امن و پویا sitemap.xml
    بدون نیاز به تغییر مدل‌ها یا ارور 500
    """
    urls = []

    # صفحات ثابت
    static_pages = ['home', 'products_list', 'articles_list', 'tutorial', 'call_us']
    for page_name in static_pages:
        try:
            url = request.build_absolute_uri(reverse(page_name))
        except:
            url = request.build_absolute_uri('/')
        urls.append(url)

    # دسته‌ها
    try:
        from .models import Category
        for category in Category.objects.all():
            try:
                url = request.build_absolute_uri(reverse('category_product', args=[category.slug]))
            except:
                url = "# URL not defined"
            urls.append(url)
    except Exception as e:
        print("Category fetch error:", e)
        print(traceback.format_exc())

    # محصولات
    try:
        from .models import Product
        for product in Product.objects.all():
            try:
                url = request.build_absolute_uri(reverse('product_detail', args=[product.slug]))
            except:
                url = "# URL not defined"
            urls.append(url)
    except Exception as e:
        print("Product fetch error:", e)
        print(traceback.format_exc())

    # ساخت XML
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for url in urls:
        xml_content += f"  <url>\n"
        xml_content += f"    <loc>{url}</loc>\n"
        xml_content += f"    <changefreq>weekly</changefreq>\n"
        xml_content += f"    <priority>0.8</priority>\n"
        xml_content += f"  </url>\n"

    xml_content += '</urlset>'

    return HttpResponse(xml_content, content_type="application/xml")