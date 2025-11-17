from django.db.models import Q
import requests
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from decimal import Decimal
from django.core.paginator import Paginator
from django.utils.text import slugify
from PIL import Image
import io
from django.core.files.base import ContentFile
from django.urls import reverse
from django.views.decorators.cache import cache_page
from .models import Category, Product, Article, Course, Order, OrderItem, AgencyRequest

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
    special_products = Product.objects.filter(special=True).order_by('-created_at')[:7]
    context = {
        'category': category,
        'products': products,
        'special_products': special_products,
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


def search_view(request):
    query = request.GET.get('q')  # q اسم input جستجو
    products = []

    if query:
        products = Product.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        ).order_by('-created_at')

    context = {
        'query': query,
        'products': products,
    }
    return render(request, 'search_results.html', context)


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


def agency_request_view(request):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        name = request.POST.get("full_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        city = request.POST.get("city", "").strip()

        # اعتبارسنجی ساده سرور
        if not all([name, phone, city]):
            return JsonResponse({"success": False})

        AgencyRequest.objects.create(
            full_name=name,
            phone=phone,
            city=city
        )
        return JsonResponse({"success": True})

    return JsonResponse({"success": False})


def dashboard_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard_home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard_home')
        else:
            messages.error(request, 'نام کاربری یا رمز عبور اشتباه است.')

    return render(request, 'dashboard/login.html')


@login_required(login_url='dashboard_login')
def dashboard_home(request):
    return render(request, 'dashboard/dashboard.html')


def dashboard_logout(request):
    logout(request)
    return redirect('dashboard_login')


# @login_required(login_url="dashboard_login")
# def dashboard_products(request):
#     products = Product.objects.select_related("category").order_by("-created_at")

#     # pagination: هر صفحه ۱۰ محصول
#     paginator = Paginator(products, 10)
#     page_number = request.GET.get("page")
#     page_obj = paginator.get_page(page_number)

#     context = {
#         "products": page_obj,
#         "page_obj": page_obj,
#     }
#     return render(request, "dashboard/sections/products.html", context)


# @login_required(login_url="dashboard_login")
# def dashboard_product_add(request):
#     """
#     افزودن محصول جدید در پنل ادمین سفارشی
#     """
#     categories = Category.objects.all()

#     if request.method == "POST":
#         # دریافت داده‌ها از فرم
#         title = request.POST.get("title", "").strip()
#         slug_input = request.POST.get("slug", "").strip()
#         slug = slugify(slug_input or title, allow_unicode=True)
#         category_id = request.POST.get("category")
#         description = request.POST.get("description", "").strip()
#         price = request.POST.get("price", "").strip()
#         features = request.POST.get("features", "").strip()
#         special = bool(request.POST.get("special"))
#         image = request.FILES.get("image")

#         # اعتبارسنجی داده‌ها
#         errors = []
#         if not title:
#             errors.append("عنوان محصول الزامی است.")
#         if not price or not price.isdigit():
#             errors.append("قیمت باید عددی باشد.")
#         if not category_id:
#             errors.append("انتخاب دسته‌بندی الزامی است.")
#         if not image:
#             errors.append("انتخاب تصویر الزامی است.")

#         # بررسی تکراری نبودن slug
#         if Product.objects.filter(slug=slug).exists():
#             errors.append("نامک (slug) وارد شده تکراری است. لطفاً مقدار دیگری انتخاب کنید.")

#         # در صورت وجود خطاها، نمایش مجدد فرم با پیام‌ها
#         if errors:
#             for e in errors:
#                 messages.error(request, e)
#             return render(request, "dashboard/sections/add_product.html", {"categories": categories})

#         # ذخیره در دیتابیس
#         category = Category.objects.get(id=category_id)
#         Product.objects.create(
#             title=title,
#             slug=slug,
#             category=category,
#             description=description,
#             price=price,
#             features=features,
#             special=special,
#             image=image,
#         )

#         messages.success(request, f"محصول «{title}» با موفقیت اضافه شد ✅")
#         return redirect("dashboard_products")

#     # نمایش فرم افزودن محصول
#     return render(request, "dashboard/sections/add_product.html", {"categories": categories})


# @login_required(login_url="dashboard_login")
# def dashboard_product_delete(request, product_id):
#     product = get_object_or_404(Product, id=product_id)

#     if request.method == "POST":
#         product.delete()
#         messages.success(request, f"محصول «{product.title}» با موفقیت حذف شد ✅")
    
#     return redirect("dashboard_products")


# @login_required(login_url="dashboard_login")
# def dashboard_product_edit(request, product_id):
#     """
#     ویرایش محصول موجود
#     """
#     product = get_object_or_404(Product, id=product_id)
#     categories = Category.objects.all()

#     if request.method == "POST":
#         title = request.POST.get("title", "").strip()
#         slug_input = request.POST.get("slug", "").strip()
#         slug = slugify(slug_input or title, allow_unicode=True)
#         category_id = request.POST.get("category")
#         description = request.POST.get("description", "").strip()
#         price = request.POST.get("price", "").strip()
#         features = request.POST.get("features", "").strip()
#         special = bool(request.POST.get("special"))
#         image = request.FILES.get("image")

#         errors = []
#         if not title:
#             errors.append("عنوان محصول الزامی است.")
#         if not price or not price.isdigit():
#             errors.append("قیمت باید عددی باشد.")
#         if not category_id:
#             errors.append("انتخاب دسته‌بندی الزامی است.")

#         # بررسی تکراری نبودن slug در محصولات دیگر
#         if Product.objects.filter(slug=slug).exclude(id=product.id).exists():
#             errors.append("نامک (slug) وارد شده تکراری است. لطفاً مقدار دیگری انتخاب کنید.")

#         if errors:
#             for e in errors:
#                 messages.error(request, e)
#             return render(request, "dashboard/sections/edit_product.html", {"categories": categories, "product": product})

#         # به‌روزرسانی فیلدها
#         product.title = title
#         product.slug = slug
#         product.category = Category.objects.get(id=category_id)
#         product.description = description
#         product.price = price
#         product.features = features
#         product.special = special
#         if image:
#             product.image = image  # فقط اگر عکس جدید انتخاب شد
#         product.save()

#         messages.success(request, f"محصول «{product.title}» با موفقیت ویرایش شد ✅")
#         return redirect("dashboard_products")

#     return render(request, "dashboard/sections/edit_product.html", {"categories": categories, "product": product})



# 🔹 تابع کمکی برای فشرده‌سازی و تبدیل WebP
def compress_and_convert_image(image_file, max_size=(1080, 1080), quality=80):
    img = Image.open(image_file)

    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    img.thumbnail(max_size, Image.LANCZOS)

    buffer = io.BytesIO()
    img.save(buffer, format="WEBP", quality=quality, optimize=True)
    buffer.seek(0)

    new_name = image_file.name.rsplit(".", 1)[0] + ".webp"
    return ContentFile(buffer.read(), name=new_name)


# -----------------------------
@login_required(login_url="dashboard_login")
def dashboard_products(request):
    products = Product.objects.select_related("category").order_by("-created_at")
    paginator = Paginator(products, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "products": page_obj,
        "page_obj": page_obj,
    }
    return render(request, "dashboard/sections/products.html", context)


@login_required(login_url="dashboard_login")
def dashboard_product_add(request):
    categories = Category.objects.all()

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        slug_input = request.POST.get("slug", "").strip()
        slug = slugify(slug_input or title, allow_unicode=True)
        category_id = request.POST.get("category")
        description = request.POST.get("description", "").strip()
        price = request.POST.get("price", "").strip()
        features = request.POST.get("features", "").strip()
        special = bool(request.POST.get("special"))
        image = request.FILES.get("image")

        errors = []
        if not title:
            errors.append("عنوان محصول الزامی است.")
        if not price or not price.isdigit():
            errors.append("قیمت باید عددی باشد.")
        if not category_id:
            errors.append("انتخاب دسته‌بندی الزامی است.")
        if not image:
            errors.append("انتخاب تصویر الزامی است.")

        if Product.objects.filter(slug=slug).exists():
            errors.append("نامک (slug) وارد شده تکراری است. لطفاً مقدار دیگری انتخاب کنید.")

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, "dashboard/sections/add_product.html", {"categories": categories})

        category = Category.objects.get(id=category_id)

        # 🔹 فشرده‌سازی و تبدیل WebP قبل از ذخیره
        if image:
            image = compress_and_convert_image(image)

        Product.objects.create(
            title=title,
            slug=slug,
            category=category,
            description=description,
            price=price,
            features=features,
            special=special,
            image=image,
        )

        messages.success(request, f"محصول «{title}» با موفقیت اضافه شد ✅")
        return redirect("dashboard_products")

    return render(request, "dashboard/sections/add_product.html", {"categories": categories})


@login_required(login_url="dashboard_login")
def dashboard_product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        product.delete()
        messages.success(request, f"محصول «{product.title}» با موفقیت حذف شد ✅")
    return redirect("dashboard_products")


@login_required(login_url="dashboard_login")
def dashboard_product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        slug_input = request.POST.get("slug", "").strip()
        slug = slugify(slug_input or title, allow_unicode=True)
        category_id = request.POST.get("category")
        description = request.POST.get("description", "").strip()
        price = request.POST.get("price", "").strip()
        features = request.POST.get("features", "").strip()
        special = bool(request.POST.get("special"))
        image = request.FILES.get("image")

        errors = []
        if not title:
            errors.append("عنوان محصول الزامی است.")
        if not price or not price.isdigit():
            errors.append("قیمت باید عددی باشد.")
        if not category_id:
            errors.append("انتخاب دسته‌بندی الزامی است.")
        if Product.objects.filter(slug=slug).exclude(id=product.id).exists():
            errors.append("نامک (slug) وارد شده تکراری است. لطفاً مقدار دیگری انتخاب کنید.")

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, "dashboard/sections/edit_product.html", {"categories": categories, "product": product})

        product.title = title
        product.slug = slug
        product.category = Category.objects.get(id=category_id)
        product.description = description
        product.price = price
        product.features = features
        product.special = special

        # 🔹 اگر تصویر جدید آپلود شد، فشرده و WebP کن
        if image:
            product.image = compress_and_convert_image(image)

        product.save()

        messages.success(request, f"محصول «{product.title}» با موفقیت ویرایش شد ✅")
        return redirect("dashboard_products")

    return render(request, "dashboard/sections/edit_product.html", {"categories": categories, "product": product})




@login_required(login_url="dashboard_login")
def dashboard_categories(request):
    categories_list = Category.objects.all().order_by("name")
    paginator = Paginator(categories_list, 10)  # هر صفحه ۱۰ دسته‌بندی
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "dashboard/sections/categories.html", {"page_obj": page_obj})


@login_required(login_url="dashboard_login")
def dashboard_category_add(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        slug_input = request.POST.get("slug", "").strip()
        slug = slugify(slug_input or name, allow_unicode=True)

        errors = []
        if not name:
            errors.append("نام دسته‌بندی الزامی است.")
        if Category.objects.filter(slug=slug).exists():
            errors.append("نامک (slug) وارد شده تکراری است.")

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, "dashboard/sections/add_category.html")

        Category.objects.create(name=name, slug=slug)
        messages.success(request, f"دسته‌بندی «{name}» با موفقیت اضافه شد ✅")
        return redirect("dashboard_categories")

    return render(request, "dashboard/sections/add_category.html")


@login_required(login_url="dashboard_login")
def dashboard_category_edit(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        slug_input = request.POST.get("slug", "").strip()
        slug = slugify(slug_input or name, allow_unicode=True)

        errors = []
        if not name:
            errors.append("نام دسته‌بندی الزامی است.")
        if Category.objects.filter(slug=slug).exclude(id=category.id).exists():
            errors.append("نامک (slug) وارد شده تکراری است.")

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, "dashboard/sections/edit_category.html", {"category": category})

        category.name = name
        category.slug = slug
        category.save()
        messages.success(request, f"دسته‌بندی «{name}» با موفقیت ویرایش شد ✅")
        return redirect("dashboard_categories")

    return render(request, "dashboard/sections/edit_category.html", {"category": category})


@login_required(login_url="dashboard_login")
def dashboard_category_delete(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == "POST":
        category.delete()
        messages.success(request, f"دسته‌بندی «{category.name}» با موفقیت حذف شد ✅")
    
    return redirect("dashboard_categories")


@login_required(login_url="dashboard_login")
def dashboard_articles(request):
    articles_list = Article.objects.all().order_by("-created_at")
    paginator = Paginator(articles_list, 10)  # هر صفحه ۱۰ مقاله
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "dashboard/sections/articles.html", {"page_obj": page_obj})


# @login_required(login_url="dashboard_login")
# def dashboard_article_add(request):
#     if request.method == "POST":
#         title = request.POST.get("title", "").strip()
#         slug_input = request.POST.get("slug", "").strip()
#         slug = slugify(slug_input or title, allow_unicode=True)
#         content = request.POST.get("content", "").strip()
#         special = bool(request.POST.get("special"))
#         image = request.FILES.get("image")

#         errors = []
#         if not title:
#             errors.append("عنوان مقاله الزامی است.")
#         if not content:
#             errors.append("متن مقاله الزامی است.")
#         if not image:
#             errors.append("انتخاب تصویر الزامی است.")
#         if Article.objects.filter(slug=slug).exists():
#             errors.append("نامک (slug) وارد شده تکراری است.")

#         if errors:
#             for e in errors:
#                 messages.error(request, e)
#             return render(request, "dashboard/sections/add_article.html")

#         Article.objects.create(
#             title=title,
#             slug=slug,
#             content=content,
#             image=image,
#             special=special
#         )

#         messages.success(request, f"مقاله «{title}» با موفقیت اضافه شد ✅")
#         return redirect("dashboard_articles")

#     return render(request, "dashboard/sections/add_article.html")


@login_required(login_url="dashboard_login")
def dashboard_article_add(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        slug_input = request.POST.get("slug", "").strip()
        slug = slugify(slug_input or title, allow_unicode=True)
        content = request.POST.get("content", "").strip()
        special = bool(request.POST.get("special"))
        image = request.FILES.get("image")

        errors = []
        if not title:
            errors.append("عنوان مقاله الزامی است.")
        if not content:
            errors.append("متن مقاله الزامی است.")
        if not image:
            errors.append("انتخاب تصویر الزامی است.")

        if Article.objects.filter(slug=slug).exists():
            errors.append("نامک (slug) وارد شده تکراری است.")

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, "dashboard/sections/add_article.html")

        # 🔹 فشرده‌سازی + تبدیل WebP ← مثل محصولات
        if image:
            image = compress_and_convert_image(image)

        Article.objects.create(
            title=title,
            slug=slug,
            content=content,
            image=image,
            special=special
        )

        messages.success(request, f"مقاله «{title}» با موفقیت اضافه شد ✅")
        return redirect("dashboard_articles")

    return render(request, "dashboard/sections/add_article.html")


# @login_required(login_url="dashboard_login")
# def dashboard_article_edit(request, article_id):
#     article = get_object_or_404(Article, id=article_id)

#     if request.method == "POST":
#         title = request.POST.get("title", "").strip()
#         slug_input = request.POST.get("slug", "").strip()
#         slug = slugify(slug_input or title, allow_unicode=True)
#         content = request.POST.get("content", "").strip()
#         special = bool(request.POST.get("special"))
#         image = request.FILES.get("image")

#         errors = []
#         if not title:
#             errors.append("عنوان مقاله الزامی است.")
#         if not content:
#             errors.append("متن مقاله الزامی است.")
#         if Article.objects.filter(slug=slug).exclude(id=article.id).exists():
#             errors.append("نامک (slug) وارد شده تکراری است.")

#         if errors:
#             for e in errors:
#                 messages.error(request, e)
#             return render(request, "dashboard/sections/edit_article.html", {"article": article})

#         article.title = title
#         article.slug = slug
#         article.content = content
#         article.special = special
#         if image:
#             article.image = image
#         article.save()

#         messages.success(request, f"مقاله «{article.title}» با موفقیت ویرایش شد ✅")
#         return redirect("dashboard_articles")

#     return render(request, "dashboard/sections/edit_article.html", {"article": article})


@login_required(login_url="dashboard_login")
def dashboard_article_edit(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        slug_input = request.POST.get("slug", "").strip()
        slug = slugify(slug_input or title, allow_unicode=True)
        content = request.POST.get("content", "").strip()
        special = bool(request.POST.get("special"))
        image = request.FILES.get("image")

        errors = []
        if not title:
            errors.append("عنوان مقاله الزامی است.")
        if not content:
            errors.append("متن مقاله الزامی است.")
        if Article.objects.filter(slug=slug).exclude(id=article.id).exists():
            errors.append("نامک (slug) وارد شده تکراری است.")

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, "dashboard/sections/edit_article.html", {"article": article})

        # 🔥 اعمال تغییرات
        article.title = title
        article.slug = slug
        article.content = content
        article.special = special

        # 🔥 اگر عکس جدید انتخاب شده → تبدیل به WebP + فشرده‌سازی
        if image:
            compressed_image = compress_and_convert_image(image)
            article.image = compressed_image

        article.save()

        messages.success(request, f"مقاله «{article.title}» با موفقیت ویرایش شد ✅")
        return redirect("dashboard_articles")

    return render(request, "dashboard/sections/edit_article.html", {"article": article})


@login_required(login_url="dashboard_login")
def dashboard_article_delete(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    if request.method == "POST":
        article.delete()
        messages.success(request, f"مقاله «{article.title}» با موفقیت حذف شد ✅")
    
    return redirect("dashboard_articles")


@login_required(login_url="dashboard_login")
def dashboard_courses(request):
    courses_list = Course.objects.all().order_by("-created_at")
    paginator = Paginator(courses_list, 10)  # هر صفحه ۱۰ آموزش
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "dashboard/sections/courses.html", {"page_obj": page_obj})


@login_required(login_url="dashboard_login")
def dashboard_course_add(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        slug_input = request.POST.get("slug", "").strip()
        slug = slugify(slug_input or title, allow_unicode=True)
        special = bool(request.POST.get("special"))
        video = request.FILES.get("video")

        errors = []
        if not title:
            errors.append("عنوان آموزش الزامی است.")
        if not video:
            errors.append("انتخاب ویدئو الزامی است.")
        if Course.objects.filter(slug=slug).exists():
            errors.append("نامک (slug) وارد شده تکراری است.")

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, "dashboard/sections/add_course.html")

        Course.objects.create(
            title=title,
            slug=slug,
            video=video,
            special=special
        )

        messages.success(request, f"آموزش «{title}» با موفقیت اضافه شد ✅")
        return redirect("dashboard_courses")

    return render(request, "dashboard/sections/add_course.html")


@login_required(login_url="dashboard_login")
def dashboard_course_edit(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        slug_input = request.POST.get("slug", "").strip()
        slug = slugify(slug_input or title, allow_unicode=True)
        special = bool(request.POST.get("special"))
        video = request.FILES.get("video")

        errors = []
        if not title:
            errors.append("عنوان آموزش الزامی است.")
        if Course.objects.filter(slug=slug).exclude(id=course.id).exists():
            errors.append("نامک (slug) وارد شده تکراری است.")

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, "dashboard/sections/edit_course.html", {"course": course})

        course.title = title
        course.slug = slug
        course.special = special
        if video:
            course.video = video
        course.save()

        messages.success(request, f"آموزش «{course.title}» با موفقیت ویرایش شد ✅")
        return redirect("dashboard_courses")

    return render(request, "dashboard/sections/edit_course.html", {"course": course})


@login_required(login_url="dashboard_login")
def dashboard_course_delete(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == "POST":
        course.delete()
        messages.success(request, f"آموزش «{course.title}» با موفقیت حذف شد ✅")
    
    return redirect("dashboard_courses")


@login_required(login_url="dashboard_login")
def dashboard_orders(request):
    orders_list = Order.objects.all().order_by("-created_at")
    paginator = Paginator(orders_list, 10)  # هر صفحه ۱۰ سفارش
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "dashboard/sections/orders.html", {"page_obj": page_obj})


@login_required(login_url="dashboard_login")
def dashboard_agency_requests(request):
    requests_list = AgencyRequest.objects.all().order_by("-created_at")
    paginator = Paginator(requests_list, 10)  # هر صفحه ۱۰ درخواست
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "dashboard/sections/agency_requests.html", {"page_obj": page_obj})
    

# Cache: 30 دقیقه
@cache_page(60 * 30)
def llm_txt(request):
    """نسخه متنی llm.txt پویا و دو زبانه"""
    base_url = 'https://www.farris.ir'

    content = f"""# LLM Manifest for Farris
# Brand: فریس (Faris)
# Description: مرجع تخصصی پلوس و سرپلوس خودرو در ایران
# زبان سایت: فارسی
# English Version Included

# Allowed URLs
"""

    # صفحات ثابت مجاز
    static_pages = ['home', 'products_list', 'articles_list', 'tutorial', 'call_us']
    for page in static_pages:
        content += f'- {request.build_absolute_uri(reverse(page))}\n'

    # صفحات دسته‌بندی
    for c in Category.objects.all():
        content += f'- {request.build_absolute_uri(c.get_absolute_url())}  # Category: {c.title}\n'

    # محصولات
    for p in Product.objects.all():
        content += f'- {request.build_absolute_uri(p.get_absolute_url())}  # Product: {p.title}\n'

    # Policy
    content += """

# Policy / AI Guardrails
# - Use only the provided URLs and product/category info.
# - Do not crawl or access cart, checkout, dashboard, payment, or search pages.
# - This file is allowed for AI reading and processing only.
"""

    return HttpResponse(content, content_type='text/plain; charset=utf-8')


@cache_page(60 * 30)
def llm_json(request):
    """نسخه JSON llm.json پویا و دو زبانه"""
    base_url = 'https://www.farris.ir'

    data = {
        'brand': {'fa': 'فریس', 'en': 'Faris'},
        'description': {
            'fa': 'مرجع تخصصی پلوس و سرپلوس خودرو در ایران با ضمانت، قیمت مناسب و ارسال سریع',
            'en': 'Specialized reference for drive shafts and CV joints in Iran with guarantee, affordable prices, and fast shipping.'
        },
        'pages': [],
        'categories': [],
        'products': [],
        'policy': {
            'allowed': 'Use only provided URLs and info',
            'restricted_pages': ['cart', 'checkout', 'dashboard', 'payment', 'search'],
            'note': 'This file is for AI processing only'
        }
    }

    # Static pages
    static_pages = ['home', 'products_list', 'articles_list', 'tutorial', 'call_us']
    for page in static_pages:
        data['pages'].append({
            'fa': request.build_absolute_uri(reverse(page)),
            'en': request.build_absolute_uri(reverse(page))
        })

    # Categories
    for c in Category.objects.all():
        data['categories'].append({
            'title_fa': c.title,
            'title_en': c.title,  # می‌توان ترجمه اضافه کرد
            'url': request.build_absolute_uri(c.get_absolute_url())
        })

    # Products
    for p in Product.objects.all():
        data['products'].append({
            'title_fa': p.title,
            'title_en': p.title,  # می‌توان ترجمه اضافه کرد
            'url': request.build_absolute_uri(p.get_absolute_url()),
            'category': p.category.title if p.category else ''
        })

    return JsonResponse(data, json_dumps_params={'ensure_ascii': False, 'indent': 2})
