from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.contrib.auth.models import User
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions
from rest_framework.authtoken.models import Token
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from videoflix import settings
from .serializers import UserSerializer, VideoSerializer
from .models import Video
from django.views.decorators.cache import cache_page


class RegisterView(APIView):    
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if User.objects.filter(email=request.data["email"]).exists():
            return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.is_valid(raise_exception=True)
        
        user = serializer.save()
        token,created  = Token.objects.get_or_create(user=user)
        
        data = {
            "user": serializer.data, 
            "token": token.key
        }
        return Response(data, status=status.HTTP_201_CREATED)
        

class LoginView(ObtainAuthToken):
    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token,created  = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user_id": user.pk, "email": user.email})
        

class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)
    


class VideoView(APIView):
    CACHETTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @cache_page(CACHETTL)
    def list(self, request):
        videos = Video.objects.all()
        serializer = VideoSerializer(videos, many=True)
    
        return Response(serializer.data)
    
    def create(self, request):
        serializer = VideoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
