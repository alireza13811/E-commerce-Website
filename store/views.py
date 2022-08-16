from django.db.models import Count
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.generics import RetrieveUpdateAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.reverse import reverse
from rest_framework.mixins import UpdateModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
import logging
from . import serializers
from . import models
from .permissions import IsAdminOrReadOnly, IsCustomerOfThisUser, IsCartOfThisUser
from .filters import ProductFilter
from .pagination import DefaultPagination

logger = logging.getLogger(__name__)


class ProductImageViewSet(ModelViewSet):
    serializer_class = serializers.ProductImageSerializer

    def get_queryset(self):
        return models.ProductImage.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}


class ProductViewSet(ModelViewSet):
    serializer_class = serializers.ProductSerializer
    queryset = models.Product.objects.prefetch_related('images').all()
    pagination_class = DefaultPagination
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update']
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter

    @method_decorator(cache_page(60 * 2))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        logger.info('Destroying Product')
        if models.OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error': 'Product cannot be deleted because it is associated with an order item.'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

        return super().destroy(request, *args, **kwargs)


class CollectionViewSet(ModelViewSet):
    serializer_class = serializers.CollectionSerializer
    queryset = models.Collection.objects.annotate(products_count=Count('products')).all()
    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        if models.Product.objects.filter(collection_id=kwargs['pk']):
            return Response({'error': 'Collection cannot be deleted because it includes one or more products.'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

        return super().destroy(request, *args, **kwargs)


class CustomerApiView(RetrieveUpdateAPIView):
    serializer_class = serializers.CustomerSerializer
    permission_classes = [IsAuthenticated, IsCustomerOfThisUser]
    # http_method_names = ['get', 'put', 'patch']
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return models.Customer.objects.all()
        return models.Customer.objects.filter(user_id=user.id)


class CustomerApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('customer-api', kwargs={'pk': request.user.customer.id}))


class CartViewSet(RetrieveModelMixin,
                  UpdateModelMixin,
                  GenericViewSet):
    serializer_class = serializers.CartSerializer
    permission_classes = [IsAuthenticated, IsCartOfThisUser]

    def get_queryset(self):
        return models.Cart.objects.filter(customer_id=self.request.user.customer.id)


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        customer = request.user.customer
        try:
            cart_id = customer.cart.id
        except models.Cart.DoesNotExist:
            cart = models.Cart.objects.create(customer_id=customer.id)
            cart.save()
            cart_id = cart.id
        return HttpResponseRedirect(reverse('cart-items-list', kwargs={'cart_pk': cart_id}))


class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [IsAuthenticated, IsCartOfThisUser]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.AddCartItemSerializer
        if self.request.method == 'PATCH':
            return serializers.UpdateCartItemSerializer
        return serializers.CartItemSerializer

    def get_queryset(self):
        return models.CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('product')

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}


class OrderViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        return models.Order.objects.filter(customer_id=self.request.user.customer.id).prefetch_related('items')

    def get_serializer_context(self):
        return {'customer_id': self.request.user.customer.id, 'cart_id': self.request.user.customer.cart.id}

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.AddOrderSerializer
        return serializers.ViewOrderSerializer
