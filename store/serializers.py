from django.db import transaction
from rest_framework import serializers
from . import models


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Collection
        fields = ['id', 'title', 'products_count']

    products_count = serializers.IntegerField(read_only=True)


class ProductSerializer(serializers.ModelSerializer):
    collection = CollectionSerializer

    class Meta:
        model = models.Product
        fields = ['title', 'price', 'description', 'inventory', 'collection', 'slug', 'promotions']


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ['title', 'price', 'description']


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Customer
        fields = ['id', 'phone', 'birth_date', 'user']
        read_only_fields = ('user',)


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    class Meta:
        model = models.CartItem
        fields = ['id', 'product_id', 'quantity']

    def validate_product_id(self, value):
        if not models.Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                'No product with the given ID was found.')
        return value

    @transaction.atomic()
    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        try:
            cart_item = models.CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except models.CartItem.DoesNotExist:
            self.instance = models.CartItem.objects.create(cart_id=cart_id, **self.validated_data)

        return self.instance


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Cart
        fields = ['items', ]


class UpdateCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.CartItem
        fields = ['product_id', 'quantity']


class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart_item):
        return cart_item.quantity * cart_item.product.price

    class Meta:
        model = models.CartItem
        fields = ['product', 'quantity', 'total_price']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OrderItem
        fields = '__all__'


class AddOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Order
        fields = ['id', 'payment_status']

    @transaction.atomic()
    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        cart_items = models.CartItem.objects.select_related('product').filter(cart_id=cart_id)
        if not cart_items:
            raise serializers.ValidationError('The cart is empty')
        order = models.Order.objects.create(customer_id=self.context['customer_id'])
        order_items = [
            models.OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.product.price
            )
            for item in cart_items
        ]
        models.OrderItem.objects.bulk_create(order_items)
        for item in cart_items:
            item.delete()

        return order


class ViewOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, order):
        return sum([item.quantity * item.unit_price for item in order.items.all()])

    class Meta:
        model = models.Order
        fields = ['id', 'payment_status', 'items', 'total_price']
