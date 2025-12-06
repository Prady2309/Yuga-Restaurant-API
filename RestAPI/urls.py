from django.urls import path, include
from . import views
from rest_framework.authtoken.views import obtain_auth_token    

urlpatterns = [
    # path('menu-items/', views.menu_items),
    path('menu-items/', views.MenuItemsView.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
    path('category/', views.CategoryView.as_view()),
    path('category/<int:pk>', views.SingleCategoryView.as_view()),
    path('groups/manager/users/', views.ManagerView, name='manager-view'),
    path('groups/manager/users/<int:userId>', views.ManagerRemove, name='manager-remove'),
    path('groups/delivery-crew/users/', views.DeliveryCrewView, name='Delivery-view'),
    path('groups/delivery-crew/users/<int:userId>', views.DeliveryRemove, name='Delivery-remove'),
    path('cart/menu-items/', views.CartView, name='cart-view'),
    path('orders/', views.OrdersView, name='order-view'),
    path('orders/<int:orderId>', views.SingleOrderView, name='single-order-view'),
]