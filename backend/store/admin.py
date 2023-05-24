from django.contrib import admin
from .models import Cart, Order, OrderItem, Product, Brand, Category, ShippingAddress

# Register your models here.
admin.site.register(Product)
admin.site.register(Brand)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
admin.site.register(Cart)
