from http.client import HTTPResponse
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from uuid import uuid4
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminOrReadOnly, IsAdminUser
from .serializers import AddCartItemSerializer, CartItemSerializer, CartSerializer, CategorySerializer, ProductSerializer, UpdateCartItemSerializer, CreateOrderSerializer, OrderSerializer
from .models import Cart, CartItem, Category, Product, Order, OrderItem
from user.models import User
# Create your views here.
# SSLCOMMERZ
from sslcommerz_lib import SSLCOMMERZ
import pprint


class SSLCOMMERZ_GATEWAY(APIView):
    def post(self, request):
        sslcommerz_settings = {
            'store_id': settings.STORE_ID,
            'store_pass': settings.STORE_PASSWORD,
            'issandbox': True
        }
        sslcommerz = SSLCOMMERZ(sslcommerz_settings)
        post_body = {}
        post_body['total_amount'] = request.data["total_amount"]
        post_body['currency'] = "BDT"
        post_body['tran_id'] = uuid4()
        post_body['success_url'] = "http://127.0.0.1:8000/sslcommerz/success/"
        post_body['fail_url'] = "http://127.0.0.1:8000/sslcommerz/failed/"
        post_body['cancel_url'] = "http://127.0.0.1:8000/sslcommerz/cancel/"
        post_body['emi_option'] = 0
        post_body['cus_name'] = request.data["cus_name"]
        post_body['cus_email'] = request.data["cus_email"]
        post_body['cus_phone'] = request.data["cus_phone"]
        post_body['cus_add1'] = request.data["cus_add1"]
        post_body['cus_city'] = request.data["cus_city"]
        post_body['cus_country'] = request.data["cus_country"]
        post_body['shipping_method'] = "NO"
        post_body['multi_card_name'] = ""
        post_body['num_of_item'] = request.data["num_of_item"]
        post_body['product_name'] = request.data["product_name"]
        post_body['product_category'] = "miscellaneous"
        post_body['product_profile'] = "miscellaneous"

        response = sslcommerz.createSession(post_body)
        pprint.pprint(response)

        return Response(response)


@csrf_exempt
def _sslcommerz_success(request):
    return redirect("http://localhost:3000/payment-success/")


@csrf_exempt
def _sslcommerz_failed(request):
    return redirect("http://localhost:3000/place-order/")


@csrf_exempt
def _sslcommerz_cancel(request):
    return redirect("http://localhost:3000/place-order/")


def index(request):
    return render(request, "sslcommerz.html", {})


@csrf_exempt
def _sslcommerz(request):
    sslcommerz_settings = {
        'store_id': settings.STORE_ID,
        'store_pass': settings.STORE_PASSWORD,
        'issandbox': True
    }
    sslcommerz = SSLCOMMERZ(sslcommerz_settings)
    post_body = {}
    post_body['tran_id'] = '5E121A0D01F92'
    post_body['val_id'] = '200105225826116qFnATY9sHIwo'
    post_body['amount'] = "10.00"
    post_body['card_type'] = "VISA-Dutch Bangla"
    post_body['store_amount'] = "9.75"
    post_body['card_no'] = "418117XXXXXX6675"
    post_body['bank_tran_id'] = "200105225825DBgSoRGLvczhFjj"
    post_body['status'] = "VALID"
    post_body['tran_date'] = "2020-01-05 22:58:21"
    post_body['currency'] = "BDT"
    post_body['card_issuer'] = "TRUST BANK, LTD."
    post_body['card_brand'] = "VISA"
    post_body['card_issuer_country'] = "Bangladesh"
    post_body['card_issuer_country_code'] = "BD"
    post_body['store_id'] = "test_testemi"
    post_body['verify_sign'] = "d42fab70ae0bcbda5280e7baffef60b0"
    post_body['verify_key'] = "amount,bank_tran_id,base_fair,card_brand,card_issuer,card_issuer_country,card_issuer_country_code,card_no,card_type,currency,currency_amount,currency_rate,currency_type,risk_level,risk_title,status,store_amount,store_id,tran_date,tran_id,val_id,value_a,value_b,value_c,value_d"
    post_body['verify_sign_sha2'] = "02c0417ff467c109006382d56eedccecd68382e47245266e7b47abbb3d43976e"
    post_body['currency_type'] = "BDT"
    post_body['currency_amount'] = "10.00"
    post_body['currency_rate'] = "1.0000"
    post_body['base_fair'] = "0.00"
    post_body['value_a'] = ""
    post_body['value_b'] = ""
    post_body['value_c'] = ""
    post_body['value_d'] = ""
    post_body['risk_level'] = "0"
    post_body['risk_title'] = "Safe"
    response = sslcommerz.hash_validate_ipn(post_body)
    pprint.pprint(response)

    return render(request, "sslcommerz.html", {
        "response": response
    })


class CategoryViewSet(ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.prefetch_related("product_set").all()


class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.select_related("brand").all()
    permission_classes = [IsAdminOrReadOnly]


class LatestProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.select_related(
        "brand").all().order_by("-updated_at")[:2]


class CartViewSet(ModelViewSet):
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.prefetch_related("cartitem_set__product").all()


class CartItemViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartItemSerializer
        if self.request.method == "PATCH":
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        return {"cart_id": self.kwargs["cart_pk"]}

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs["cart_pk"]).select_related("product")


class OrderViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_permissions(self):
        if self.request.method in ["PATCH", "DELETE"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Order.objects.prefetch_related("orderitem_set").select_related("shippingaddress").all().order_by("-created_at")

        user_id = User.objects.only(
            "id").get(id=user.id)
        return Order.objects.prefetch_related("orderitem_set").select_related("shippingaddress").filter(user_id=user_id).order_by("-created_at")

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data, context={
                                           "user_id": self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateOrderSerializer
        # if self.request.method == "PATCH":
        #     return UpdateOrderSerializer
        return OrderSerializer
