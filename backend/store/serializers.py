from dataclasses import fields
from venv import create
from rest_framework.serializers import ModelSerializer, SerializerMethodField, UUIDField
from rest_framework import serializers
from django.db import transaction
from user.models import User
from user.serializers import UserSerializer
from .models import Cart, CartItem, Category, Order, OrderItem, Product, ShippingAddress


class SimpleCategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "title"]


class ProductSerializer(ModelSerializer):
    brand_title = SerializerMethodField(method_name="get_brand_title")
    category = SimpleCategorySerializer(many=True)

    def get_brand_title(self, product: Product):
        return product.brand.title

    class Meta:
        model = Product
        fields = ["id", "user", "title", "brand_title", "category", "image", "description", "price",
                  "stock_count", "rating", "review_count"]


class CategorySerializer(ModelSerializer):
    product_set = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["id", "title", "product_set"]


class CartItemSerializer(ModelSerializer):
    product = ProductSerializer()
    total_price = SerializerMethodField(method_name="get_total_price")

    def get_total_price(self, cart_item: CartItem):
        return cart_item.product.price * cart_item.quantity

    class Meta:
        model = CartItem
        fields = ["id", "cart", "product", "quantity", "total_price"]


class CartSerializer(ModelSerializer):
    id = UUIDField(read_only=True)
    cartitem_set = CartItemSerializer(many=True, read_only=True)
    total_price = SerializerMethodField(method_name="get_total_price")
    total_quantity = SerializerMethodField(method_name="get_total_quantity")

    def get_total_price(self, cart: Cart):
        return sum([item.quantity * item.product.price for item in cart.cartitem_set.all()])

    def get_total_quantity(self, cart: Cart):
        return sum([item.quantity for item in cart.cartitem_set.all()])

    class Meta:
        model = Cart
        fields = ["id", "created_at", "cartitem_set",
                  "total_price", "total_quantity"]


class AddCartItemSerializer(ModelSerializer):
    product_id = serializers.IntegerField()

    def save(self, **kwargs):
        cart_id = self.context["cart_id"]
        product_id = self.validated_data["product_id"]
        quantity = self.validated_data["quantity"]
        try:
            cart_item = CartItem.objects.get(
                cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(
                cart_id=cart_id, **self.validated_data)

        return self.instance

    class Meta:
        model = CartItem
        fields = ["id", "product_id", "quantity"]


class UpdateCartItemSerializer(ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["quantity"]


class ShippingAddressSerializer(ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ["id", "address", "city", "postal_code", "country"]


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "price"]


class OrderSerializer(ModelSerializer):
    user = UserSerializer()
    orderitem_set = OrderItemSerializer(many=True)
    shippingaddress = ShippingAddressSerializer()

    class Meta:
        model = Order
        fields = ["id", "user", "created_at", "payment_method", "tax_price",
                  "shipping_price", "total_price", "is_paid", "paid_at", "is_delivered", "delivered_at", "orderitem_set", "shippingaddress"]


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()
    payment_method = serializers.CharField()
    tax_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    shipping_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    address = serializers.CharField()
    city = serializers.CharField()
    postal_code = serializers.CharField()
    country = serializers.CharField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError(
                "No cart with the given ID was found.")
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError("The cart is empty.")
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            user_id = self.context["user_id"]
            cart_id = self.validated_data["cart_id"]
            payment_method = self.validated_data["payment_method"]
            tax_price = self.validated_data["tax_price"]
            shipping_price = self.validated_data["shipping_price"]
            total_price = self.validated_data["total_price"]
            address = self.validated_data["address"]
            city = self.validated_data["city"]
            postal_code = self.validated_data["postal_code"]
            country = self.validated_data["country"]

            print(address, city, postal_code, country)

            # getting the customer by user_id
            user = User.objects.get(id=user_id)

            # creating order with the above customer
            order = Order.objects.create(
                user=user,
                payment_method=payment_method,
                tax_price=tax_price,
                shipping_price=shipping_price,
                total_price=total_price,
                is_paid=True
            )

            ShippingAddress.objects.create(
                order=order,
                address=address,
                city=city,
                postal_code=postal_code,
                country=country
            )

            # getting cart items by cart_id
            cart_items = CartItem.objects.select_related(
                "product").filter(cart_id=cart_id)

            # creating order items to save in database
            order_items = [
                OrderItem(
                    user=user,
                    order=order,
                    product=item.product,
                    price=item.product.price,
                    quantity=item.quantity
                ) for item in cart_items
            ]

            # saving cart items to database
            OrderItem.objects.bulk_create(order_items)

            # deleting existing cart
            Cart.objects.filter(pk=cart_id).delete()

            return order
