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

    path('dashboard/login/', views.dashboard_login, name='dashboard_login'),
    path('dashboard/logout/', views.dashboard_logout, name='dashboard_logout'),
    path('dashboard/', views.dashboard_home, name='dashboard_home'),
    path("dashboard/products/", views.dashboard_products, name="dashboard_products"),
    path("dashboard/products/add/", views.dashboard_product_add, name="dashboard_product_add"),
    path("dashboard/products/delete/<int:product_id>/", views.dashboard_product_delete, name="dashboard_product_delete"),
    path("dashboard/products/edit/<int:product_id>/", views.dashboard_product_edit, name="dashboard_product_edit"),

    path("dashboard/categories/", views.dashboard_categories, name="dashboard_categories"),
    path("dashboard/categories/add/", views.dashboard_category_add, name="dashboard_category_add"),
    path("dashboard/categories/edit/<int:category_id>/", views.dashboard_category_edit, name="dashboard_category_edit"),
    path("dashboard/categories/delete/<int:category_id>/", views.dashboard_category_delete, name="dashboard_category_delete"),

    path("dashboard/articles/", views.dashboard_articles, name="dashboard_articles"),
    path("dashboard/articles/add/", views.dashboard_article_add, name="dashboard_article_add"),
    path("dashboard/articles/edit/<int:article_id>/", views.dashboard_article_edit, name="dashboard_article_edit"),
    path("dashboard/articles/delete/<int:article_id>/", views.dashboard_article_delete, name="dashboard_article_delete"),

    # path('dashboard/', views.dashboard, name="dashboard"),
    # path('dashboard/load/<str:section>/', views.load_dashboard_section, name="load_dashboard_section"),
    # path('dashboard/products/create/', views.create_product, name="create_product"),
    # path('dashboard/products/update/', views.update_product, name="update_product"),
    # path('dashboard/products/delete/<int:pk>/', views.delete_product, name="delete_product"),
]