from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('/category/<slug:slug>/', views.category_product, name='category_product'),
    path('/products', views.products_list, name='products_list'),
    path('/products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('/articles', views.articles_list, name='articles_list'),
    path('/articles/<slug:slug>/', views.article_detail, name='article_detail'),
    path('/callus', views.call_us, name='call_us'),
]