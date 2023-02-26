from django.shortcuts import render
from django.contrib.auth.models import User
from LittleLemonAPI.models import Category, MenuItem
from LittleLemonAPI.paginations import MenuItemsPagination
from LittleLemonAPI.serializers import CategorySerializer, MenuItemSerializer
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


@api_view()
@permission_classes([IsAuthenticated])
def secret(request):
    return Response({"message": "Secret message"}, status=status.HTTP_200_OK)