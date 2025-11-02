from .models import Category

def categories_context(request):
    """
    این تابع تمام دسته‌بندی‌ها را به صورت خودکار
    در اختیار تمام قالب‌ها قرار می‌دهد.
    """
    categories = Category.objects.all().order_by('name')
    return {'categories': categories}