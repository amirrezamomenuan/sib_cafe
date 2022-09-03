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
        foods = Food.objects.get_page(int(request.GET.get("page", 1)))
        serialized_data = self.serializer_class(foods, many = True)
        return Response(data = serialized_data.data, status=status.HTTP_200_OK)    


class MenuView(APIView):
    serializer_class = FoodItemserializer
    permission_classes = [IsAuthenticated, ]

    def get(self, request, day):
        food_items = FoodItem.objects.show_menu(day)
        serialized_data = self.serializer_class(food_items, many= True)
        # print(len(connection.queries))
        return Response(data= serialized_data.data, status = status.HTTP_200_OK)


# TODO: add pagination
class OrderView(APIView):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        order_id = request.GET.get('order_id')
        if order_id is not None:
            order_item = get_object_or_404(OrderItem, pk = order_id, user = request.user)
            serialized_data = self.serializer_class(order_item)
        else:
            order_items = OrderItem.objects.filter(user = request.user)
            serialized_data = self.serializer_class(order_items, many= True)
        return Response(data=serialized_data.data, status=status.HTTP_200_OK)


    # def post(self, request):
    #     serializer_data = self.serializer_class(data=request.data)
    #     if serializer_data.is_valid(raise_exception=True):
    #         serializer_data.save()

    # def delete(self, request):
    #     pass




# class FoodRateView(APIView):
#     serializer_class = None
#     permission_classes = [IsAuthenticated, ]

#     def post(self, request):
#         pass