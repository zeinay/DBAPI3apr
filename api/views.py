from django.shortcuts import render
from rest_framework.generics import ListAPIView,RetrieveAPIView,RetrieveUpdateAPIView,DestroyAPIView,CreateAPIView
from .serializers import (ItemListSerializer, ItemDetailSerializer,UserCreateSerializer,OrderUpdateSerializer,OrderSerializer,
    CartCreateSerializer,CartListSerializer,UserUpdateSerializer,ItemCreateSerializer,CartUpdateSerializer)
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from api.models import Item, Cart, Order
from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
import json
from django.core import serializers


class UserCreateAPIView(CreateAPIView):
    serializer_class = UserCreateSerializer

class UserUpdateView(RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'user_id'

class ItemListView(ListAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemListSerializer
    filter_backends = [SearchFilter,OrderingFilter]
    search_fields = ['name','description','price','category']

class ItemDetailView(RetrieveAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemDetailSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'item_id'


class OrderUpdateView(RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderUpdateSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'order_id'


class CartListView(ListAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartListSerializer
    filter_backends = [SearchFilter]
    search_fields = ['order',]

class CartCreateAPIView(CreateAPIView):
    serializer_class = CartCreateSerializer

class CartUpdateView(RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = CartUpdateSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'card_id'

class ItemCreateAPIView(CreateAPIView):
    serializer_class = ItemCreateSerializer



class OrderControlAPIView(APIView):
    
    def post(self,request,item_id):

        try:
            items = Item.objects.get(id = item_id)
        except Item.DoesNotExist:
            items = None   
            return Response(items)
        try:
            orders = Order.objects.get(user= request.user, status=0)
            serializer = OrderSerializer(orders, many=False)
        except Order.DoesNotExist:
            orders=None

        if (orders):
            try:
                carts = Cart.objects.get(order = orders , item = items)
            except Cart.DoesNotExist:
                carts=None

            if(carts):
                self.UpdateCart(cart_id = carts.id,new_quantity = carts.quantity + 1)
            else:
               self.CreateCart(order = orders,item = items,item_price = items.price)

        else:
            orders = self.CreateOrder(item = items,item_price = items.price)
            serializer = OrderSerializer(orders, many=False)

        return Response(serializer.data)

  # Update the quantity of the cart item 
    def UpdateCart(self,cart_id,new_quantity):
        try:
            Cart.objects.filter(id = cart_id).update(quantity= new_quantity)
        except Cart.DoesNotExist:
            return None     

# Create order and cart item 
    def CreateOrder(self,item,item_price):  
        orders= Order.objects.create(user=self.request.user,date = timezone.now(),status = 0,total = item_price)
        self.CreateCart(order = orders,item = item,item_price = item_price)
        return orders

    def CreateCart(self,order,item,item_price):
        carts= Cart.objects.create(item= item,order=order,price = item_price ,quantity = 1)
        return carts





    






