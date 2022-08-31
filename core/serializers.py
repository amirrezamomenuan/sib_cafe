from rest_framework import serializers

from core.models import Food

class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = ['name', 'description', 'category', ]