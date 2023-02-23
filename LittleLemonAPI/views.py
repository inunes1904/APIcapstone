from django.shortcuts import render
from django.contrib.auth.models import User
from LittleLemonAPI.models import MenuItem
from LittleLemonAPI.serializers import MenuItemSerializer
from rest_framework import generics
from rest_framework.permissions import IsAdminUser


# Create your views here.
class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer