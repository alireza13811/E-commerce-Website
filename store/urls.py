from django.urls import path, include, re_path
from rest_framework_nested import routers
from django.views.decorators.cache import cache_page
from . import views

router = routers.DefaultRouter()
router.register('products', views.ProductViewSet, basename='products')
router.register('collections', views.CollectionViewSet, basename='collections')
router.register('carts', views.CartViewSet, basename='carts')
router.register('orders', views.OrderViewSet, basename='orders')

product_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
product_router.register('images', views.ProductImageViewSet, basename='images')

cart_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
cart_router.register('items', views.CartItemViewSet, basename='cart-items')


urlpatterns = [
    path('customer/', views.CustomerApi.as_view()),
    path('customer/<int:pk>/', views.CustomerApiView.as_view(), name='customer-api'),
    path('carts/', views.CartView.as_view()),
]
urlpatterns += router.urls + cart_router.urls + product_router.urls
