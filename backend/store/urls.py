from cgitb import lookup
from django.urls import path, include
from . import views
from rest_framework_nested import routers


router = routers.DefaultRouter()
router.register("products", views.ProductViewSet, basename="products")
router.register("latest-products", views.LatestProductViewSet,
                basename="latest-products")
router.register("categories", views.CategoryViewSet, basename="categories")
router.register("carts", views.CartViewSet, basename="carts")


carts_router = routers.NestedDefaultRouter(router, "carts", lookup="cart")
carts_router.register("items", views.CartItemViewSet,
                      basename="cart-items")
router.register("orders", views.OrderViewSet, basename="orders")

urlpatterns = [
    path('', include(router.urls)),
    path('', include(carts_router.urls)),
    path("store/", views.index, name="home"),
    path("sslcommerz-ipn", views._sslcommerz, name="sslcommerz-ipn"),
    path("sslcommerz/", views.SSLCOMMERZ_GATEWAY.as_view(), name="sslcommerz"),
    path("sslcommerz/success/", views._sslcommerz_success,
         name="sslcommerz-success"),
    path("sslcommerz/failed/", views._sslcommerz_failed, name="sslcommerz-failed"),
    path("sslcommerz/cancel/", views._sslcommerz_cancel, name="sslcommerz-cancel")
]
