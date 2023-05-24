from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.hashers import make_password
from .serializers import CreateUserSerializer, MyTokenObtainPairSerializer, UserSerializer
from .models import User


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class UserViewSet(ModelViewSet):
    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateUserSerializer
        return UserSerializer

    queryset = User.objects.all()
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=["POST"], permission_classes=[AllowAny])
    def register(self, request):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=["GET", "PUT"], permission_classes=[IsAuthenticated])
    def me(self, request):
        (user, created) = User.objects.get_or_create(id=request.user.id)
        if request.method == "GET":
            serializer = UserSerializer(user, many=False)
            return Response(serializer.data)
        if request.method == "PUT":
            serializer = UserSerializer(user, many=False)
            user.password = make_password(request.data["password"])
            user.first_name = request.data["first_name"]
            user.last_name = request.data["last_name"]
            user.phone = request.data["phone"]
            user.save()
            return Response(serializer.data)
