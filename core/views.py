from django.shortcuts import get_object_or_404
from django.db import connection

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from core.serializers import FoodItemserializer, FoodListSerializer, FoodSerializer, OrderItemSerializer
from core.models import Food, FoodItem, OrderItem


class FoodView(APIView):
    serializer_class = FoodSerializer
    permission_classes = [IsAuthenticated,]

    def get(self, request, food_id):
        food = get_object_or_404(Food, pk = food_id)
        serialized_data = self.serializer_class(food)
        return Response(data = serialized_data.data, status=status.HTTP_200_OK)


class FoodListView(APIView):
    serializer_class = FoodListSerializer
    permission_classes = [IsAuthenticated,]

    def get(self, request):
        page = int(request.GET.get("page", 1))
        foods = Food.objects.get_page(page)
        serialized_data = self.serializer_class(foods, many = True)
        return Response(data = serialized_data.data, status=status.HTTP_200_OK)    


class MenuView(APIView):
    serializer_class = FoodItemserializer
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        weekday = request.GET.get('weekday')
        if weekday is None:
            # change this to limit passed week days
            return Response(data= {'days' : [0, 1, 2, 3, 4]}, status = status.HTTP_200_OK)

        page = int(request.GET.get("page", 1))
        food_items = FoodItem.objects.show_menu(weekday).get_page(page)
        serialized_data = self.serializer_class(food_items, many= True)
        return Response(data= serialized_data.data, status = status.HTTP_200_OK)


# TODO: add pagination
class ShowOrdersView(APIView):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        order_items = OrderItem.objects.filter(user = request.user)
        serialized_data = self.serializer_class(order_items, many= True)
        return Response(data=serialized_data.data, status=status.HTTP_200_OK)




# class FoodRateView(APIView):
#     serializer_class = None
#     permission_classes = [IsAuthenticated, ]

#     def post(self, request):
#         pass