from django.shortcuts import render, get_object_or_404
from .models import Category, Product, Article, Course
from django.core.paginator import Paginator


def home(request):
    categories = Category.objects.all()
    special_products = Product.objects.filter(special=True).order_by('-created_at')[:7]
    special_courses = Course.objects.filter(special=True).order_by('-created_at')[:6]
    special_articles = Article.objects.filter(special=True).order_by('-created_at')[:4]

    context = {
        'categories': categories,
        'special_products': special_products,
        'special_courses': special_courses,
        'special_articles': special_articles,
    }

    return render(request, 'home.html', context)


def category_product(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.all().order_by('-created_at')  # از related_name استفاده کردیم
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'category_product.html', context)


def products_list(request):
    products = Product.objects.all().order_by('-created_at')
    special_products = Product.objects.filter(special=True).order_by('-created_at')[:7]
    categories = Category.objects.all()  # برای فیلتر یا نمایش در سایدبار

    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'products': products,
        'special_products': special_products,
        'categories': categories,
        'page_obj': page_obj,
    }
    return render(request, 'products.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)

    keywords = product.title.split()

    related_products = Product.objects.none()
    for word in keywords:
        related_products |= Product.objects.filter(title__icontains=word)

    related_products = related_products.exclude(id=product.id).distinct()[:3]

    context = {
        'product': product,
        'related_products': related_products,
    }

    return render(request, 'single_product.html', context)


def articles_list(request):
    articles = Article.objects.all().order_by('-created_at')
    special_articles = Article.objects.filter(special=True).order_by('-created_at')[:7]
    paginator = Paginator(articles, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    first_pages = range(1, min(4, paginator.num_pages + 1))

    context = {
        'articles': articles,
        'special_articles': special_articles,
        "page_obj": page_obj,
        "first_pages": first_pages,
    }
    return render(request, 'articles.html', context)

def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug)

    keywords = article.title.split()

    related_articles = Article.objects.none()
    for word in keywords:
        related_articles |= Article.objects.filter(title__icontains=word)

    related_articles = related_articles.exclude(id=article.id).distinct()[:3]

    context = {
        'article': article,
        'related_articles': related_articles,
    }

    return render(request, 'single_article.html', context)


def tutorial(request):
    tutorials = Course.objects.all().order_by('-created_at')
    special_tutorials = Course.objects.filter(special=True).order_by('-created_at')[:7]
    categories = Category.objects.all()

    paginator = Paginator(tutorials, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'tutorials': tutorials,
        'special_tutorials': special_tutorials,
        'page_obj': page_obj,
    }
    return render(request, 'tutorial.html', context)


def call_us(request):
    categories = Category.objects.all()

    context = {
        'categories': categories,
    }
    return render(request, 'call_us.html' , context)