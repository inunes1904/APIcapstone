from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User, Group
from LittleLemonAPI.models import Category, MenuItem, Cart
from LittleLemonAPI.paginations import MenuItemsPagination
from LittleLemonAPI.serializers import CartDeleteSerializer, CartSerializer, CategorySerializer, ManagerSerializer, MenuItemSerializer
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics, status
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from .permissions import IsManager, IsDeliveryCrew


# Create your views here.
class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    search_fields = ['title', 'category__title']
    ordering_fields = ['price', 'category']
    pagination_class = MenuItemsPagination

    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    
    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.method == 'PATCH':
            permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
        if self.request.method == 'DELETE':
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes] 
    
    def patch(self, request, *args, **kwargs):
        menuitem = MenuItem.objects.get(pk=self.kwargs['pk'])
        menuitem.feature = not menuitem.feature
        menuitem.save()
        return Response( {'message':f'Featured status of {str(menuitem.title)}' 
                          +f'changed to {str(menuitem.feature)}'}, status=status.HTTP_200_OK)

class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

class ManagersView(generics.ListCreateAPIView):
    queryset = User.objects.filter(groups__name='Manager')
    serializer_class = ManagerSerializer
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]

    def post(self, request, *args, **kwargs):
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name='Manager')
            managers.user_set.add(user)
            return Response({'message':'User added to the Manager Group'},
                            status= status.HTTP_201_CREATED)
        return Response({'message': 'Something went wrong'},
                         status.HTTP_400_BAD_REQUEST)

class SingleManagerView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.filter(groups__name='Manager')
    serializer_class = ManagerSerializer
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def delete(self, request, *args, kwargs):
        pk = self.kwargs['pk']
        user = get_object_or_404(User, pk=pk)
        managers = User.objects.get(name='Manager')
        managers.user_set.remove(user)
        return Response({'message': 'User removed from Manager group'},
                        status=status.HTTP_200_OK)

class DeliveryCrewsView(generics.ListCreateAPIView):
    queryset = User.objects.filter(groups__name='Delivery crew')
    serializer_class = ManagerSerializer
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def post(self, request, *args, **kwargs):
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            crew = User.objects.get(name='Delivery crew')
            crew.user_set.add(user)
            return Response({'message': 'User added to the Delivery Crew Group'},
                            status= status.HTTP_201_CREATED)
        return Response({'message': 'Something went wrong'},
                         status.HTTP_400_BAD_REQUEST)

class SingleDeliveryCrewsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.filter(groups__name='Delivery crew')
    serializer_class = ManagerSerializer
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        user = get_object_or_404(User, pk=pk)
        managers = Group.objects.get(name='Delivery crew')
        managers.user_set.remove(user)
        return Response({'message': 'User removed from the Delivery crew group'},
                        status=status.HTTP_200_OK)

class CartView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        cart = Cart.objects.filter(user=self.request.user)
        return cart
    
    def post(self, request, *args, **kwargs):
        serialized_item = CartSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        id = request.data['menuitem']
        quantity = request.data['quantity']
        item = get_object_or_404(MenuItem, id=id)
        price = int(quantity) * item.price
        try:
            Cart.objects.create(user=request.user, quantity=quantity,
                                unit_price=item.price, price=price,
                                 menuitem=id )
        except:
            return Response({'message': 'Item is already in cart'}, 
                             status=status.HTTP_409_CONFLICT)
        return Response({'message': 'Item was added to cart'}, 
                         status=status.HTTP_201_CREATED)
    
    def delete(self, request, *args, **kwargs):
        if request.data['menuitem']:
            serialized_item = CartDeleteSerializer(data=request.data)
            serialized_item.is_valid(raise_exception=True)
            menuitem = request.data['menuitem']
            cart = get_object_or_404(Cart, user=request.user, menuitem=menuitem)
            cart.delete()
            return Response({'message':'Item was removed from your cart'},
                            status=status.HTTP_200_OK)
        else:
            Cart.objects.filter(user=request.user).delete()
            return Response({'message':'All items were removed' 
                             +'from your cart'}, status=status.HTTP_201_CREATED)



@api_view()
@permission_classes([IsAuthenticated])
def secret(request):
    return Response({"message": "Secret message"}, status=status.HTTP_200_OK)