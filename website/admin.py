from django.contrib import admin
from .models import Category, Product, Article, Course


# --------------------
# تنظیمات نمایش Category
# --------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


# --------------------
# تنظیمات نمایش Product
# --------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "price", "special", "created_at")
    prepopulated_fields = {"slug": ("title",)}
    list_filter = ("category",)
    search_fields = ("title", "description")
    ordering = ("-created_at",)



@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "special", "created_at")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "summary", "content")
    ordering = ("-created_at",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "special", "created_at")
    prepopulated_fields = {"slug": ("title",)}
    list_filter = ("special",)
    search_fields = ("title",)
    ordering = ("-created_at",)