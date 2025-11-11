from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('category/<slug:slug>/', views.category_product, name='category_product'),
    path('products/', views.products_list, name='products_list'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('articles/', views.articles_list, name='articles_list'),
    path('articles/<slug:slug>/', views.article_detail, name='article_detail'),
    path('tutorial/', views.tutorial, name='tutorial'),
    path('call_us/', views.call_us, name='call_us'),
    path('cart/', views.cart_page, name='cart_page'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/increase/<int:product_id>/', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:product_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('order-success/<str:tracking_code>/', views.order_success, name='order_success'),
    path('payment/<int:order_id>/', views.zarinpal_payment, name='zarinpal_payment'),
    path('payment/verify/<int:order_id>/', views.zarinpal_verify, name='zarinpal_verify'),
    path('search/', views.search_view, name='search'),
    path('agency-request/', views.agency_request_view, name='agency_request'),
    # path("dashboard/", views.dashboard, name="dashboard"),
    # path("dashboard/load/<str:section>/", views.load_dashboard_section, name="load_dashboard_section"),
    # # مسیرهای CRUD محصول
    # path("dashboard/products/create/", views.create_product, name="create_product"),
    # path("dashboard/products/update/", views.update_product, name="update_product"),
    # path("dashboard/products/delete/<int:pk>/", views.delete_product, name="delete_product"),
    # داشبورد اصلی
    path('dashboard/', views.dashboard, name="dashboard"),
    path('dashboard/load/<str:section>/', views.load_dashboard_section, name="load_dashboard_section"),
    path('dashboard/products/create/', views.create_product, name="create_product"),
    path('dashboard/products/update/', views.update_product, name="update_product"),
    path('dashboard/products/delete/<int:pk>/', views.delete_product, name="delete_product"),
]