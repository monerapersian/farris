from django.contrib import admin
from .models import Category, Product, Article, Course, Order, OrderItem


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


# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ("full_name", "phone", "total_price", "created_at")
#     list_filter = ("full_name",)
#     search_fields = ("full_name",)
#     ordering = ("-created_at",)


# @admin.register(OrderItem)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ("order", "product_title", "quantity", "price")
#     list_filter = ("order",)
#     search_fields = ("order",)
#     ordering = ("-order",)


# تعریف Inline برای نمایش محصولات هر سفارش
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # هیچ ردیف اضافی ایجاد نشه
    readonly_fields = ('product_title', 'quantity', 'price')  # فقط نمایش داده بشه

# ثبت مدل Order و اتصال Inline
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'tracking_code', 'total_price', 'created_at', 'phone')
    inlines = [OrderItemInline]