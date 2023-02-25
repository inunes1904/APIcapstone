from rest_framework import serializers
from .models import MenuItem, Category
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class MenuItemSerializer(serializers.ModelSerializer):
    category_id = CategorySerializer(write_only=True)
    category = CategorySerializer(read_only=False)
    class Meta:
        model = MenuItem 
        fields = '__all__'
        extra_kwargs = {
            'price': {'min_value': 0.1}
        }

class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = []
        

