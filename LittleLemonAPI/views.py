from django.shortcuts import render
from django.contrib.auth.models import User
from LittleLemonAPI.models import Category, MenuItem
from LittleLemonAPI.serializers import CategorySerializer, MenuItemSerializer
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework import status, generics, permissions


# Create your views here.
class MenuItemsView(APIView):
    
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, format=None):
        snippets = MenuItem.objects.all()
        serializer = MenuItemSerializer(snippets, many=True)
        return Response(serializer.data)
    
    
    def post(self, request, format=None):
        serializer = MenuItemSerializer(data=request.data)
        if serializer.is_valid():
            if request.user.groups.filter(name='Admin').exists():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.data, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoriesView(APIView):
    
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, format=None):
        snippets = Category.objects.all()
        serializer = CategorySerializer(snippets, many=True)
        return Response(serializer.data)
    
    
    def post(self, request, format=None):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            if request.user.groups.filter(name='Admin').exists():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.data, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view()
@permission_classes([IsAuthenticated])
def secret(request):
    return Response({"message": "Secret message"})