from django.db.models import Count
from django.http import HttpResponseRedirect
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.generics import RetrieveUpdateAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.reverse import reverse
from rest_framework.mixins import UpdateModelMixin, RetrieveModelMixin
from . import serializers
from . import models
from .permissions import IsAdminOrReadOnly, IsCustomerOfThisUser, IsCartOfThisUser


class ProductViewSet(ModelViewSet):
    serializer_class = serializers.ProductSerializer
    queryset = models.Product.objects.all()
    permission_classes = [IsAdminOrReadOnly]


class CollectionViewSet(ModelViewSet):
    serializer_class = serializers.CollectionSerializer
    queryset = models.Collection.objects.annotate(products_count=Count('products')).all()
    permission_classes = [IsAdminOrReadOnly]


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
    permission_classes = [IsAuthenticated, IsCartOfThisUser]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.AddCartItemSerializer
        return serializers.UpdateCartItemSerializer

    def get_queryset(self):
        return models.CartItem.objects.filter(cart_id=self.kwargs['cart_pk'])

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}


class OrderViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return models.Order.objects.filter(customer_id=self.request.user.customer.id)

    def get_serializer_context(self):
        return {'customer_id': self.request.user.customer.id, 'cart_id': self.request.user.customer.cart.id}

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.AddOrderSerializer
        return serializers.ViewOrderSerializer


class OrderItemViewSet(ModelViewSet):
    serializer_class = serializers.OrderItemSerializer

    def get_queryset(self):
        return models.OrderItem.objects.filter(order_id=self.kwargs['order_pk'])

    def get_serializer_context(self):
        return {'order_id': self.kwargs['order_pk']}


