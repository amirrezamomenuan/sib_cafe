from datetime import date, datetime
from django.shortcuts import get_object_or_404
from django.db import connection

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from core.serializers import CreateOrderSerializer, FoodItemDetailSerializer, FoodItemserializer, FoodListSerializer, FoodSerializer, OrderItemSerializer
from core.models import Food, FoodItem, OrderItem


#finished menu
class MenuView(APIView):
    serializer_class = FoodItemserializer
    permission_classes = [AllowAny, ]

    def get(self, request):
        food_items = FoodItem.objects.show_menu(**request.query_params).get_page(**request.query_params)
        if not food_items.exists():
            return Response(status= status.HTTP_404_NOT_FOUND)

        serialized_data = self.serializer_class(food_items, many= len(food_items) > 1)
        return Response(data= serialized_data.data, status = status.HTTP_200_OK)

# finished menuitem
class MenuItemView(APIView):
    serializer_class = FoodItemDetailSerializer
    permission_classes = [AllowAny, ]

    def get(self, request):
        menu_item_id = request.query_params.get('menu_item_id')
        fooditem = get_object_or_404(FoodItem, pk=menu_item_id)
        serialized_data = self.serializer_class(fooditem)
        return Response(data=serialized_data.data, status=status.HTTP_200_OK)


class CreateOrderView(APIView):
    serializer_class = CreateOrderSerializer # TODO: change serializer
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        serialized_data = self.serializer_class(data= request.data)
        food_item = get_object_or_404(FoodItem, pk=serialized_data.initial_data.get('food_item_id'))
        # order_date = date(data.initial_data.get('order_date'))

        serialized_data.is_valid()
        order_date = serialized_data.validated_data.get('order_date')
        if food_item.can_be_ordered(request.user, order_date=order_date):
            print('it can be ordered')
            new_order = OrderItem(food_item = food_item, user=request.user, last_modifier = 0, order_date = order_date)
            new_order.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            print('it cannot be ordered')
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)


class ShowOrdersView(APIView):
    serializer_class = OrderItemSerializer # TODO: change serializer
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        page = int(request.GET.get("page", 1))
        order_items = OrderItem.objects.get_user_orders(user= request.user).get_page(page)
        serialized_data = self.serializer_class(order_items, many= True)
        return Response(data=serialized_data.data, status=status.HTTP_200_OK)


class ShowOrderView(APIView):
    serializer_class = OrderItemSerializer # TODO: change serializer
    permission_classes = [IsAuthenticated, ] # TODO: add permission to check if order belongs to request.user

    def get(self, request, order_id):
        order_item = get_object_or_404(OrderItem, pk = order_id)
        serialized_data = self.serializer_class(order_item)
        return Response(data=serialized_data.data, status=status.HTTP_200_OK)


class CancelOrderView(APIView):
    serializer_class = OrderItemSerializer # TODO: change serializer
    permission_classes = [IsAuthenticated, ] # TODO: add permission to check if order belongs to request.user

    def put(self, request):
        pass


class FoodView(APIView):
    serializer_class = FoodSerializer
    permission_classes = []

    def get(self, request):
        food_id = request.GET.get('food_id')
        offset = int(request.GET.get("offset", 0))
        limit = int(request.GET.get("limit", 100))
        if food_id is not None:
            food = get_object_or_404(Food, pk = food_id)
            serialized_data = self.serializer_class(food)
        else:
            # foods = Food.objects.get_page(page)
            foods = Food.objects.all()[offset: limit + offset]
            if foods.count() == 0:
                return Response(data = {"message": "food does not exist with your limit and offset"}, status = 416)
            serialized_data = self.serializer_class(foods, many = True)
        return Response(data = serialized_data.data, status=status.HTTP_200_OK)   


class FoodListView(APIView):
    serializer_class = FoodSerializer
    permission_classes = [IsAuthenticated,]

    def get(self, request):
        page = int(request.GET.get("page", 1))
        foods = Food.objects.get_page(page)
        serialized_data = self.serializer_class(foods, many = True)
        return Response(data = serialized_data.data, status=status.HTTP_200_OK)    

# class FoodRateView(APIView):
#     serializer_class = None
#     permission_classes = [IsAuthenticated, ]

#     def post(self, request):
#         pass