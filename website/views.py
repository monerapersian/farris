import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from decimal import Decimal
from .models import Category, Product, Article, Course, Order, OrderItem
from django.core.paginator import Paginator

# MERCHANT_ID = "34e4ca8c-11fe-4bb5-a897-9f73d78f4dac"
# ZARINPAL_REQUEST_URL = "https://sandbox.zarinpal.com/pg/v4/payment/request.json"
# ZARINPAL_START_URL = "https://sandbox.zarinpal.com/pg/StartPay/"
# ZARINPAL_VERIFY_URL = "https://sandbox.zarinpal.com/pg/v4/payment/verify.json"
MERCHANT_ID = "8192cbc6-b8c0-4e14-acbf-474e7d9b1dcb"
ZARINPAL_REQUEST_URL = "https://api.zarinpal.com/pg/v4/payment/request.json"
ZARINPAL_START_URL = "https://www.zarinpal.com/pg/StartPay/"
ZARINPAL_VERIFY_URL = "https://api.zarinpal.com/pg/v4/payment/verify.json"


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
    return render(request, 'master.html', context)


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
    special_articles = Article.objects.filter(special=True).order_by('-created_at')[:4]

    paginator = Paginator(tutorials, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'tutorials': tutorials,
        'special_articles': special_articles,
        'page_obj': page_obj,
    }
    return render(request, 'tutorial.html', context)


def call_us(request):
    categories = Category.objects.all()

    context = {
        'categories': categories,
    }
    return render(request, 'call_us.html' , context)


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # اگر هنوز سبد خرید وجود نداره، بسازش
    cart = request.session.get('cart', {})

    # اگر محصول قبلاً اضافه شده، تعدادش رو زیاد کن
    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += 1
    else:
        cart[str(product_id)] = {
            'title': product.title,
            'category': str(product.category),
            'price': int(product.price),
            'image': product.image.url if product.image else '',
            'quantity': 1,
        }

    # ذخیره در سشن
    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart_page')


def cart_page(request):
    cart = request.session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    return render(request, 'shopping_cart.html', {'cart': cart, 'total': total})

@require_POST
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
        request.session.modified = True
    return redirect('cart_page')


def increase_quantity(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += 1
        request.session['cart'] = cart
        request.session.modified = True
    return redirect('cart_page')


def decrease_quantity(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        if cart[str(product_id)]['quantity'] > 1:
            cart[str(product_id)]['quantity'] -= 1
        else:
            # اگر به صفر رسید، حذف کن
            del cart[str(product_id)]
        request.session['cart'] = cart
        request.session.modified = True
    return redirect('cart_page')


# def checkout_view(request):
#     cart = request.session.get('cart', {})
#     if not cart:
#         messages.warning(request, "سبد خرید شما خالی است!")
#         return redirect('cart_page')

#     total_price = sum(Decimal(item['price']) * item['quantity'] for item in cart.values())

#     if request.method == 'POST':
#         full_name = request.POST.get('full_name')
#         phone = request.POST.get('phone')
#         address = request.POST.get('address')
#         accept_terms = request.POST.get('accept_terms')

#         if not full_name or not phone or not address:
#             messages.error(request, "لطفاً تمام فیلدها را پر کنید.")
#             return redirect('checkout')

#         if accept_terms != 'on':
#             messages.error(request, "برای ادامه باید قوانین را بپذیرید.")
#             return redirect('checkout')

#         # ایجاد سفارش با وضعیت پرداخت نشده
#         order = Order.objects.create(
#             full_name=full_name,
#             phone=phone,
#             address=address,
#             total_price=total_price,
#         )

#         # حالا مستقیم ریدایرکت به زarinpal_payment
#         return redirect('zarinpal_payment', order_id=order.id)

#     return render(request, 'checkout.html', {'cart': cart, 'total': total_price})


def checkout_view(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, "سبد خرید شما خالی است!")
        return redirect('cart_page')

    total_price = sum(Decimal(item['price']) * item['quantity'] for item in cart.values())

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        accept_terms = request.POST.get('accept_terms')

        if not full_name or not phone or not address:
            messages.error(request, "لطفاً تمام فیلدها را پر کنید.")
            return redirect('checkout')

        if accept_terms != 'on':
            messages.error(request, "برای ادامه باید قوانین را بپذیرید.")
            return redirect('checkout')

        # ایجاد سفارش با وضعیت پرداخت نشده
        order = Order.objects.create(
            full_name=full_name,
            phone=phone,
            address=address,
            total_price=total_price,
            is_paid=False  # ← اگر فیلد مدل داری
        )

        # ثبت محصولات در OrderItem
        for item in cart.values():
            OrderItem.objects.create(
                order=order,
                product_title=item['title'],
                category=item.get('category', ''),  # ← اگر دسته‌بندی داری
                price=Decimal(item['price']),
                quantity=item['quantity']
            )

        # هدایت مستقیم به صفحه پرداخت
        return redirect('zarinpal_payment', order_id=order.id)

    return render(request, 'checkout.html', {'cart': cart, 'total': total_price})


def order_success(request, tracking_code):
    order = get_object_or_404(Order, tracking_code=tracking_code)
    return render(request, 'payment_success.html', {'order': order})


# def payment_success(request, tracking_code):
#     order = Order.objects.filter(tracking_code=tracking_code).first()
#     return render(request, 'payment_success.html', {'order': order})


def payment_failed(request, tracking_code=None):
    order = None
    if tracking_code:
        order = Order.objects.filter(tracking_code=tracking_code).first()
    return render(request, 'payment_failed.html', {'order': order})


def zarinpal_payment(request, order_id):
    order = Order.objects.get(id=order_id)
    callback_url = request.build_absolute_uri(f"/payment/verify/{order.id}/")

    data = {
        "merchant_id": MERCHANT_ID,
        "amount": int(order.total_price),  # مبلغ به تومان
        "callback_url": callback_url,
        "description": f"خرید از فریس - سفارش {order.tracking_code}",
        "metadata": {"mobile": order.phone},
        "currency": "IRT"
    }

    try:
        response = requests.post(ZARINPAL_REQUEST_URL, json=data, timeout=10)
        result = response.json()
        if result['data']['code'] == 100:
            authority = result['data']['authority']
            return redirect(f"{ZARINPAL_START_URL}{authority}")
        else:
            messages.error(request, "خطا در ایجاد تراکنش، لطفاً دوباره تلاش کنید.")
            return redirect('checkout')
    except Exception as e:
        messages.error(request, f"خطای ارتباط با زرین‌پال: {str(e)}")
        return redirect('checkout')


def zarinpal_verify(request, order_id):
    order = Order.objects.get(id=order_id)
    status = request.GET.get('Status')
    authority = request.GET.get('Authority')

    if status != 'OK':
        messages.error(request, "پرداخت شما ناموفق بود.")
        return redirect('checkout')

    data = {
        "merchant_id": MERCHANT_ID,
        "amount": int(order.total_price),
        "authority": authority
    }

    try:
        response = requests.post(ZARINPAL_VERIFY_URL, json=data, timeout=10)
        result = response.json()
        if result['data']['code'] == 100:
            # پرداخت موفق
            order.is_paid = True
            order.save()
            # پاک کردن سبد خرید
            request.session['cart'] = {}
            request.session.modified = True
            return redirect('order_success', tracking_code=order.tracking_code)
        else:
            messages.error(request, "پرداخت شما ناموفق بود.")
            return redirect('checkout')
    except Exception as e:
        messages.error(request, f"خطا در تایید پرداخت: {str(e)}")
        return redirect('checkout')