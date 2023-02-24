from django.urls import path, include
from . import views

urlpatterns = [
    path('menu-items', views.MenuItemsView.as_view()),
    path('categories', views.CategoriesView.as_view()),
    path('secret', views.secret),
    path('api-auth/', include('rest_framework.urls')),
 
]
