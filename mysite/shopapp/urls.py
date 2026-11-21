from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import LatestProductsFeed

from django.contrib.sitemaps.views import sitemap
from shopapp.sitemaps import ShopSitemap

from .views import LatestProductsFeed
from . import views

from .views import (
    ShopIndexView,
    ProductDetailsView,
    ProductsListView,
    OrdersListView,
    OrderDetailView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    ProductsDataExportView,
    ProductViewSet,
    OrderViewSet,
    UserOrdersListView,
)

app_name = "shopapp"

router = DefaultRouter()
router.register(
    r"products",
    ProductViewSet,
    basename="product",
)
router.register(
    r"orders",
    OrderViewSet,
    basename="order",
)

sitemaps = {
    "shop": ShopSitemap,
}


urlpatterns = [
    path("", ShopIndexView.as_view(), name="index"),
    path("products/", ProductsListView.as_view(), name="products_list"),
    path("products/export/", ProductsDataExportView.as_view(), name="products-export"),
    path("products/create/", ProductCreateView.as_view(), name="product_create"),
    path("products/<int:pk>/", ProductDetailsView.as_view(), name="product_details"),
    path("products/<int:pk>/update/", ProductUpdateView.as_view(), name="product_update"),
    path("products/<int:pk>/archive/", ProductDeleteView.as_view(), name="product_delete"),
    path("orders/", OrdersListView.as_view(), name="orders_list"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order_details"),

    path(
        "api/",
        include(router.urls),
    ),

    path(
        "products/latest/feed/",
        LatestProductsFeed(),
        name="latest-products-feed",
    ),

    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),

    path(
        "users/<int:user_id>/orders/",
        UserOrdersListView.as_view(),
        name="user-orders",
    ),

    path(
        "users/<int:user_id>/orders/export/",
        views.user_orders_export,
        name="user-orders-export",
    ),
]