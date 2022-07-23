from django.db import models
from django.contrib.auth import get_user_model


class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount = models.FloatField()


class Collection(models.Model):
    title = models.CharField(max_length=255)


class Product(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    slug = models.SlugField()
    description = models.TextField(null=True, blank=True)
    inventory = models.IntegerField()
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT, related_name='products')
    promotions = models.ManyToManyField(Promotion, blank=True)
    last_update = models.DateTimeField(auto_now=True)


class Cart(models.Model):
    data_created = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    quantity = models.PositiveSmallIntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class Customer(models.Model):
    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=True, blank=True)
    cart = models.OneToOneField(Cart, on_delete=models.PROTECT)
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)


class Wishlist(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.PROTECT)


class WishlistItem(models.Model):
    products = models.ForeignKey(Product, models.CASCADE)
    wishlist = models.ForeignKey(Wishlist, models.CASCADE)


class Order(models.Model):
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
        (PAYMENT_STATUS_FAILED, 'Failed')
    ]
    payment_status = models.CharField(max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    data_created = models.DateTimeField(auto_now_add=True)


class orderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
