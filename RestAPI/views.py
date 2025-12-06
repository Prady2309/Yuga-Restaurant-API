from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, generics, status
from datetime import date

# For generics and viewsets 
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination

from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import api_view, renderer_classes, permission_classes, throttle_classes
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.contrib.auth.models import User, Group

# For Function based View
from django.core.paginator import Paginator, EmptyPage

from .models import MenuItem, Category, Order, OrderItem, Cart
from .serializers import CategorySerializer, MenuItemSerializer, CartSerializer, OrderItemSerializer, OrderSerializer

from rest_framework.permissions import DjangoModelPermissions, DjangoModelPermissionsOrAnonReadOnly # DRF will check the user’s group permissions automatically.


# Create your views here.
class MenuItemsView(generics.ListCreateAPIView):                        # For all Menu Items
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'price']
    search_fields = ['title']
    ordering_fields = ['id', 'price']
    ordering = ['id']

class SingleMenuItemView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):    # For single Menu Item
    queryset = MenuItem.objects.select_related('category').all()        
    serializer_class = MenuItemSerializer
    permission_classes = [DjangoModelPermissions]


class CategoryView(generics.ListCreateAPIView):                        # For all Category
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title']
    ordering = ['id']

class SingleCategoryView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):    # For single Category
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [DjangoModelPermissions]


# User Group Management Endpoints
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def ManagerView(request):
    if request.user.is_superuser or request.user.groups.filter(name__in=['Admin', 'Manager']).exists():
        if request.method == 'GET':
            # user_groups = request.user.groups.values_list('name', flat=True)  # Get names of groups a user belongs to
            manager = Group.objects.get(name='Manager')
            manager_users = manager.user_set.all().values('id', 'username', 'first_name', 'last_name', 'email')
            return Response(manager_users, status=status.HTTP_200_OK)
        
        if request.method == 'POST':
            username = request.data.get('username')
            if username:
                user = get_object_or_404(User, username=username)
                manager = Group.objects.get(name='Manager')
                if user.groups.filter(name='Manager').exists():
                    return Response('User is already a Manager.', status=status.HTTP_400_BAD_REQUEST)
                manager.user_set.add(user)
                return Response(f'User {username} added successfully.', status=status.HTTP_200_OK)
            return Response('Bad Request', status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response("You don't have the permissions to do this operation", status=status.HTTP_403_FORBIDDEN)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def ManagerRemove(request, userId):
    if request.user.is_superuser or request.user.groups.filter(name__in=['Admin', 'Manager']).exists():
        user = get_object_or_404(User, id=userId)
        manager = Group.objects.get(name='Manager')

        if user.groups.filter(name='Manager').exists():
            manager.user_set.remove(user)
            return Response(f'User {user.username} removed successfully.', status=status.HTTP_200_OK)
        return Response('User is not a Manager.', status=status.HTTP_400_BAD_REQUEST)    
    else:
        return Response("You don't have the permissions to do this operation", status=status.HTTP_403_FORBIDDEN)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def DeliveryCrewView(request):
    if request.user.groups.filter(name__in=['Admin', 'Manager']).exists():
        if request.method == 'GET':
            delivery = Group.objects.get(name='Delivery')
            delivery_users = delivery.user_set.all().values('id', 'username', 'first_name', 'last_name', 'email')
            return Response(delivery_users, status=status.HTTP_200_OK)
        
        if request.method == 'POST':
            username = request.data.get('username')
            if username:
                user = get_object_or_404(User, username=username)
                delivery = Group.objects.get(name='Delivery')
                if user.groups.filter(name='Delivery').exists():
                    return Response('User is already in Delivery Crew.', status=status.HTTP_400_BAD_REQUEST)
                delivery.user_set.add(user)
                return Response(f'User {username} added successfully.', status=status.HTTP_200_OK)
            return Response({"details": "Username field missing"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"detail": "You don't have the permissions to do this operation"}, status=status.HTTP_403_FORBIDDEN)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def DeliveryRemove(request, userId):
    if request.user.is_superuser or request.user.groups.filter(name__in=['Admin', 'Manager']).exists():
        user = get_object_or_404(User, id=userId)
        delivery = Group.objects.get(name='Delivery')

        if user.groups.filter(name='Delivery').exists():
            delivery.user_set.remove(user)
            return Response(f'User {user.username} removed successfully.', status=status.HTTP_200_OK)
        return Response('User is not a Delivery Crew.', status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'detail': "You don't have the permissions to do this operation"}, status=status.HTTP_403_FORBIDDEN)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def CartView(request):
    if not request.user.groups.filter(name='Customer').exists():
        return Response("You don't have the permissions to do this operation", status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        cart_items = Cart.objects.select_related('menuitem', 'menuitem__category').filter(user=request.user)
        serializer = CartSerializer(cart_items, many=True, context={'request': request})
        total = sum(item.price for item in cart_items)
        # return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({
            'items': serializer.data,
            'total_items': cart_items.count(),
            'total_price': total
        }, status=status.HTTP_200_OK)

    if request.method == 'POST':
        menuitem_id = request.data.get('menuitem_id')
        quantity = request.data.get('quantity')
        if not menuitem_id or not quantity:
            return Response({"details": "menuitem_id and quantity fields are required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            menuitem = MenuItem.objects.get(id=menuitem_id)
        except MenuItem.DoesNotExist:
            return Response({"details": "Menu item not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if item already exists in cart for this user
        cart_items, created = Cart.objects.get_or_create(
            user=request.user, 
            menuitem=menuitem, 
            defaults={
                'quantity': quantity,
                'unit_price': menuitem.price,
                'price': menuitem.price * int(quantity)
            }
        )

        if not created:
            # If it exists, update the quantity and price
            cart_items.quantity += int(quantity)
            cart_items.price = cart_items.unit_price * cart_items.quantity
            cart_items.save()

        serializer = CartSerializer(cart_items, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    if request.method == 'DELETE':
        cart_items = Cart.objects.filter(user=request.user)
        cart_items.delete()
        return Response(f'Cart deleted successfully.', status=status.HTTP_200_OK)


# ---------------- /api/orders/ -- ORDER VIEW --------------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def OrdersView(request):
    if request.method == 'GET':
        if request.user.groups.filter(name__in=['Admin', 'Manager']).exists() or request.user.is_superuser:
            orders = Order.objects.all()
        else:
            orders = Order.objects.filter(user=request.user)
        
        serializer = OrderSerializer(orders, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    if request.method == 'POST':
        if not request.user.groups.filter(name='Customer').exists():
            return Response("Only customers can create orders", status=status.HTTP_403_FORBIDDEN)
        
        cart_items = Cart.objects.select_related('menuitem').filter(user=request.user)
        if not cart_items.exists():
            return Response({"details": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)
    
        # Create Order
        order = Order.objects.create(
            user=request.user, 
            total=sum(item.price for item in cart_items),
            date=date.today())
        
        # Create OrderItems from Cart
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price)
        
        # Clear Cart
        cart_items.delete()
        
        serializer = OrderSerializer(order, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# ---------------- /api/orders/{orderID} -- SINGLE ORDER VIEW --------------
@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def SingleOrderView(request, orderId):
    if request.method == 'GET':
        if request.user.groups.filter(name__in=['Customer', 'Manager']).exists():
            order = Order.objects.filter(user=request.user, id=orderId)
            serializer = OrderSerializer(order, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response("Only Customers/Managers can view orders", status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'POST':
        pass

    if request.method == 'PUT':
        pass

    if request.method == 'PATCH':
        pass

    if request.method == 'DELETE':
        order = get_object_or_404(Order, id=orderId)
        all_orders = Order.objects.all()
        delivery = Group.objects.get(name='Delivery')

        if request.user.groups.filter(name=['Manager']).exists():
            all_orders.remove(order)
            return Response(f"Order - {orderId} deleted.", status=status.HTTP_200_OK)
        return Response("Only Managers can delete orders", status=status.HTTP_403_FORBIDDEN)
        
    

# @api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
# def menu_items(request):             # fields = ['id', 'title', 'price', 'featured', 'category']
#     if request.method == 'GET':
#         menu_items = MenuItem.objects.select_related('category').all()
#         # Filters, Order Params
#         category_name = request.query_params.get('category')
#         from_price = request.query_params.get('fromPrice', default=0.0)
#         to_price = request.query_params.get('toPrice')
#         search = request.query_params.get('search')
#         order = request.query_params.get('orderBy')
#         perpage = request.query_params.get('perpage', default=10)   # 10 rows per page
#         page = request.query_params.get('page', default=1)          # page 1 by default
        
#         if category_name:                                                       # Filtering
#             menu_items = menu_items.filter(category__title=category_name)
#         if to_price:
#             # menu_items = menu_items.filter(price=to_price)
#             menu_items = menu_items.filter(price__range=(from_price, to_price))
#         if search:
#             menu_items = menu_items.filter(category__contains=search)

#         if order:                                                           # Ordering
#             ordering_fields = order.split(",")
#             menu_items = menu_items.order_by(*ordering_fields)

#         paginator = Paginator(menu_items, per_page=perpage)
#         try:
#             menu_items = paginator.page(number=page)
#         except EmptyPage:
#             menu_items = []
#         except Exception:
#             return Response({'detail': 'Invalid page number.'}, status=status.HTTP_400_BAD_REQUEST)

#         serialized_item = MenuItemSerializer(menu_items, many=True, context={'request': request})
        
#         if request.user.groups.filter(name='Customer').exists():
#             return Response(serialized_item.data, status=status.HTTP_200_OK)
#         else:
#             return Response(serialized_item.data, status=status.HTTP_200_OK)
#             # return Response({
#             #     'data': serialized_item.data,
#             #     'page': menu_items.number,
#             #     'perpage': paginator.per_page,
#             #     'total_pages': paginator.num_pages,
#             #     'total_items': paginator.count
#             # }, status=status.HTTP_200_OK)
        
#     if request.method == 'POST':
#         serialized_item = MenuItemSerializer(data=request.data, context={'request': request})
#         if request.user.is_superuser or request.user.groups.filter(name='Manager').exists():
#             # serialized_item = MenuItemSerializer(data=request.data, context={'request': request})
#             serialized_item.is_valid(raise_exception=True)                  # Validations
#             serialized_item.save()                                          # Save into DB
#             return Response(serialized_item.data, status.HTTP_201_CREATED) 
#         else:
#             return Response('Unauthorized - Access Denied', status=status.HTTP_403_FORBIDDEN)


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def category_all(request):             # fields = ['id', 'title', 'price', 'featured', 'category']
#     if request.method == 'GET':
#         menu_items = Category.objects.select_related('category').all()
#         # Filters, Order Params
#         category_name = request.query_params.get('category')
#         from_price = request.query_params.get('fromPrice', default=0.0)
#         to_price = request.query_params.get('toPrice')
#         search = request.query_params.get('search')
#         order = request.query_params.get('orderBy')
#         perpage = request.query_params.get('perpage', default=10)   # 10 rows per page
#         page = request.query_params.get('page', default=1)          # page 1 by default
        
#         if category_name:                                                       # Filtering
#             menu_items = menu_items.filter(category__title=category_name)
#         if to_price:
#             # menu_items = menu_items.filter(price=to_price)
#             menu_items = menu_items.filter(price__range=(from_price, to_price))
#         if search:
#             menu_items = menu_items.filter(category__contains=search)

#         if order:                                                           # Ordering
#             ordering_fields = order.split(",")
#             menu_items = menu_items.order_by(*ordering_fields)

#         paginator = Paginator(menu_items, per_page=perpage)
#         try:
#             menu_items = paginator.page(number=page)
#         except EmptyPage:
#             menu_items = []
#         except Exception:
#             return Response({'detail': 'Invalid page number.'}, status=status.HTTP_400_BAD_REQUEST)

#         serialized_item = MenuItemSerializer(menu_items, many=True, context={'request': request})
        
#         if request.user.groups.filter(name='Customer').exists():
#             return Response(serialized_item.data, status=status.HTTP_200_OK)
#         else:
#             return Response({
#                 'data': serialized_item.data,
#                 'page': menu_items.number,
#                 'perpage': paginator.per_page,
#                 'total_pages': paginator.num_pages,
#                 'total_items': paginator.count
#             }, status=status.HTTP_200_OK)
