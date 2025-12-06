from rest_framework import serializers
from .models import MenuItem, Category, Order, OrderItem, Cart
from decimal import Decimal
from rest_framework.validators import UniqueTogetherValidator 
from django.contrib.auth.models import User, Group

"""
Sending Data Out (Serialization): 
Your Product object needs to be converted into JSON so a web browser can display it.

Receiving Data In (Deserialization): 
When a user sends data (e.g., to create a new product), that data usually arrives as JSON. 
You need to convert it back into a Python object that Django can work with and then save it to your database.
"""

# For Group
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']         # group name

# For User
class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)
    class Meta:
        model = User
        fields = ['id', 'first_name', 'username', 'groups']

# ------------------------------------------------------------------------------------------------------------------ #

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']
        

class MenuItemSerializer(serializers.ModelSerializer):
    # For Input/Writing (ID field)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',    # Used category field in MenuItem model
        write_only=True
    )

    # Output/Reading (Entire Category object)
    category = CategorySerializer(read_only=True)      # Show category title (not just ID)

    class Meta:
        model = MenuItem
        # fields = ['id', 'title', 'price', 'featured', 'category']
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    menuitem_id = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all(),
        source='menuitem',
        write_only=True
    )
    menuitem = MenuItemSerializer(read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'menuitem', 'menuitem_id', 'quantity', 'unit_price', 'price']
        read_only_fields = ['user']  # User is set automatically from request
    
    def create(self, validated_data):
        # Automatically set unit_price and price from menuitem
        menuitem = validated_data['menuitem']
        quantity = validated_data['quantity']
        
        validated_data['unit_price'] = menuitem.price
        validated_data['price'] = menuitem.price * quantity
        
        return super().create(validated_data)
    

# Order Summary
class OrderItemSerializer(serializers.ModelSerializer):
    menuitem_id = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all(),
        source='menuitem',
        write_only=True
    )
    menuitem = MenuItemSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'menuitem_id', 'menuitem', 'quantity', 'unit_price', 'price']
        read_only_fields = ['unit_price', 'price']

# After Ordering
class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    delivery_crew = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(groups__name="Delivery"),
        required=False,
        allow_null=True
    )
    class Meta: 
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date']
        read_only_fields = ['user', 'total', 'date']