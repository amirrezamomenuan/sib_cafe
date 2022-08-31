from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.serializers import FoodSerializer
from core.models import Food

class FoodListView(APIView):
    serializer_class = FoodSerializer
    permission_classes = [AllowAny,]

    def get(self, request):
        foods = Food.objects.all()
        data = FoodSerializer(foods, many = True)
        return Response(data = data.data, status=200)