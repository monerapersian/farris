from django.db import models


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