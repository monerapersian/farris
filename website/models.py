from django.db import models
import uuid


# --------------------
# دسته‌بندی محصولات
# --------------------
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام دسته‌بندی")
    slug = models.SlugField(unique=True, verbose_name="نامک (Slug)")

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"

    def __str__(self):
        return self.name


# --------------------
# محصولات
# --------------------
class Product(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان محصول")
    slug = models.SlugField(unique=True, verbose_name="نامک (Slug)")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products", verbose_name="دسته‌بندی")
    description = models.TextField(verbose_name="توضیحات")
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="قیمت (تومان)")
    image = models.ImageField(upload_to="products/", verbose_name="تصویر")
    features = models.TextField(
        "ویژگی‌ها",
        blank=True,
        help_text="ویژگی‌ها را با '|' جدا کنید. حداکثر ۹ ویژگی."
    )
    special = models.BooleanField(default=False, verbose_name="ویژه")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        ordering = ["-created_at"]

    def get_features_list(self):
        """لیست ویژگی‌ها به صورت array"""
        if not self.features:
            return []
        return [f.strip() for f in self.features.split("|") if f.strip()][:9]

    def __str__(self):
        return self.title


class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان مقاله")
    slug = models.SlugField(unique=True, verbose_name="نامک (Slug)")
    content = models.TextField(verbose_name="متن کامل مقاله")
    image = models.ImageField(upload_to="articles/", verbose_name="تصویر مقاله")
    special = models.BooleanField(default=False, verbose_name="ویژه")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ انتشار")

    class Meta:
        verbose_name = "مقاله"
        verbose_name_plural = "مقالات"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان آموزش")
    slug = models.SlugField(unique=True, verbose_name="نامک (Slug)")
    video = models.FileField(upload_to="courses/videos/", verbose_name="ویدئو")
    special = models.BooleanField(default=False, verbose_name="ویژه")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ انتشار")

    class Meta:
        verbose_name = "آموزش"
        verbose_name_plural = "آموزش‌ها"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


from django.db import models


class Order(models.Model):
    full_name = models.CharField(max_length=100, verbose_name="نام و نام خانوادگی")
    phone = models.CharField(max_length=11, verbose_name="شماره تماس")
    address = models.TextField(verbose_name="آدرس")
    total_price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="جمع فاکتور")
    tracking_code = models.CharField(
        max_length=12,
        unique=True,
        editable=False,
        verbose_name="کد پیگیری"
    )
    is_paid = models.BooleanField(default=False, verbose_name="پرداخت شده")  # ← اضافه کن
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت سفارش")

    def save(self, *args, **kwargs):
        if not self.tracking_code:
            self.tracking_code = str(uuid.uuid4().hex[:12]).upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"سفارش {self.full_name} ({self.tracking_code})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="سفارش")
    product_title = models.CharField(max_length=200, verbose_name="نام محصول")
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="قیمت واحد")
    quantity = models.PositiveIntegerField(default=1, verbose_name="تعداد")
    image = models.URLField(blank=True, null=True, verbose_name="تصویر محصول")

    def __str__(self):
        return f"{self.product_title} (x{self.quantity})"