from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response

from core.serializers import FoodSerializer
from core.models import Food


class FoodView(APIView):
    serializer_class = FoodSerializer
    permission_classes = [IsAuthenticated,]

    def get(self, request, food_id):
        food = get_object_or_404(Food, pk = food_id)
        data = FoodSerializer(food)
        return Response(data = data.data, status=200)

