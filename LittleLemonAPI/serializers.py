from rest_framework import serializers
from .models import Cart, MenuItem, Category, Order, Rating
from django.contrib.auth.models import User
from rest_framework.validators import UniqueTogetherValidator


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
        fields = ['id', 'title', 'price']

class CartSerializer(serializers.ModelSerializer):
    menuitem = CartItemSerializer()
    class Meta:
        fields = ['menuitem', 'quantity', 'price']

class CartPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['menuitem', 'quantity']
        extra_kwargs = {
            'quantity': { 'min_value': 1 }
        }

class CartDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fieds = ['menuitem']
        
class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), default=serializers.CurrentUserDefault())
    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total', 'delivery_crew', 'date']

class OrderItemSerializer(serializers.Serializer):
    class Meta:
        model = MenuItem
        fields = ['title', 'price']
        
class SingleOrderSerializer(serializers.ModelSerializer):
    menuitem = OrderItemSerializer()
    class Meta:
        model = Order
        fields = ['menuitem', 'quantity']

class EditOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['delivery_crew']

class RatingSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),
                                              default=serializers.CurrentUserDefault())
    class Meta:
        model = Rating
        fields = ['user', 'menuitem', 'rating']
        validators = [UniqueTogetherValidator(queryset=Rating.objects.all(), 
                                              fields=['user', 'menuitem', 'rating'])]
        extra_kwargs = {'rating': {'min_value':0, 'max_value': 5}}