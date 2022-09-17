from datetime import date
from rest_framework import serializers

from core.models import Food, FoodItem, OrderItem

class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = ['name', 'description', 'category', "image", ]


class FoodListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = ['name', "image",]


class FoodItemserializer(serializers.ModelSerializer):
    food = FoodListSerializer()
    class Meta:
        model = FoodItem
        fields = ['id', 'amount', 'price', 'food']


class FoodItemDetailSerializer(serializers.ModelSerializer):
    food = FoodSerializer()
    class Meta:
        model = FoodItem
        fields = ['id', 'amount', 'price', 'weekday', 'food']


class OrderItemSerializer(serializers.ModelSerializer):
    food_item = FoodItemserializer()

    class Meta:
        model = OrderItem
        fields = ['food_item', 'time_submited', 'last_modified', 'state', ]
        

class CreateOrderSerializer(serializers.Serializer):
    food_item_id = serializers.IntegerField()
    order_date = serializers.DateField()


class CancelOrderSerializer(serializers.Serializer):
    order_item_id = serializers.IntegerField()


class OrderItemDetailSerializer(serializers.ModelSerializer):
    food_item = FoodItemserializer()
    class Meta:
        model = OrderItem
        fields = ['food_item', 'state', 'order_date', 'time_submited']