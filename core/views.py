from datetime import date

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q


from core.serializers import (CancelOrderSerializer,
                            CreateOrderSerializer,
                            FoodItemDetailSerializer,
                            FoodItemserializer,
                            OrderItemSerializer,
                            OrderItemDetailSerializer,
                            RateSubmittionSerializer,
                            )
from core.models import FoodItem, FoodRate, OrderItem
from core.utils import get_object_or_404_rest, LeaderBoardRedisClient


class MenuView(ListAPIView):
    serializer_class = FoodItemserializer
    permission_classes = [AllowAny, ]
    pagination_class = LimitOffsetPagination
    queryset = FoodItem.objects.all()
    default_limit = 60

    def get_queryset(self):
        order_parameter = self.request.query_params.get('order_by', '-creation_time')
        week_day = self.request.query_params.get('weekday')
        if week_day:
            week_day = int(week_day[0])
        else:
            week_day = (date.weekday(date.today()) + 2) % 7
        
        if week_day in (5, 6):
            return self.queryset.none()

        # TODO: check if food can be ordered
        queryset = self.queryset.filter(Q(weekday= week_day) | Q(weekday = -1))
        return queryset.order_by(order_parameter)


class MenuItemView(APIView):
    serializer_class = FoodItemDetailSerializer
    permission_classes = [AllowAny, ]

    def get(self, request):
        menu_item_id = request.query_params.get('menu_item_id')
        fooditem = get_object_or_404_rest(FoodItem, pk=menu_item_id)
        if fooditem:
            serialized_data = self.serializer_class(fooditem)
            return Response(data=serialized_data.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)


class CreateOrderView(APIView):
    serializer_class = CreateOrderSerializer
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        serialized_data = self.serializer_class(data= request.data)
        if serialized_data.is_valid():
            order_item = OrderItem(user = request.user, **serialized_data.validated_data)
            if order_item.can_be_submitted():
                order_item.submit()
                return Response(status=status.HTTP_201_CREATED)
            else:
                return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)


class CancelOrderView(APIView):
    serializer_class = CancelOrderSerializer
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        serialized_data = self.serializer_class(data=request.data)
        if serialized_data.is_valid():
            order_item = get_object_or_404_rest(OrderItem.objects.select_related('food_item', 'food_item__food'), pk = serialized_data.validated_data.get('order_item_id'))
            if order_item:
                if order_item.can_be_canceled(request.user):
                    order_item.cancel_order(request.user)
                    return Response(status=status.HTTP_200_OK)
                return Response(status=status.HTTP_403_FORBIDDEN)
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class OrderDetailView(APIView):
    serializer_class = OrderItemDetailSerializer
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        order_id = request.query_params.get('order_id')
        order_item = get_object_or_404_rest(OrderItem, pk=order_id, user=request.user)
        if order_item:
            serialized_data = self.serializer_class(order_item)
            return Response(data=serialized_data.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)


class OrderListView(ListAPIView):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated, ]
    pagination_class = LimitOffsetPagination
    queryset = OrderItem.objects.all()
    default_limit = 50

    def get_queryset(self):
        return self.queryset.filter(user = self.request.user)


class FoodRateView(APIView):
    serializer_class = RateSubmittionSerializer
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        serialized_data = self.serializer_class(data=request.data)
        if serialized_data.is_valid():
            food_rate_item = FoodRate(user=request.user, **serialized_data.validated_data)
            if food_rate_item.can_be_submitted():
                food_rate_item.save()
                return Response(status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class LeaderBoardView(APIView):
    def get(self, request):
        data = LeaderBoardRedisClient().get_leader_board()
        print(data)
        print(len(data))
        if data:
            return Response(data=data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)