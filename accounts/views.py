from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


from accounts.serializers import SignupSerializer, TokenObtainPairSerializer, TokenObtainSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


class SignupView(APIView):
    serializer_class = SignupSerializer
    permission_classes = []

    def post(self, request):
        serializer_data = SignupSerializer(data=request.data)
        if serializer_data.is_valid():
            serializer_data.save()
            # TODO: replace with redirect
            token_serializer_data = TokenObtainPairSerializer(data = serializer_data.validated_data)
            if token_serializer_data.is_valid():
                print(token_serializer_data.validated_data)
                return Response(data = token_serializer_data.validated_data, status=status.HTTP_200_OK)

        print(serializer_data.errors)
        print(type(serializer_data.error_messages))
        print(serializer_data.validated_data)
        print("\n\n\n")
        return Response(data= serializer_data.errors, status= status.HTTP_406_NOT_ACCEPTABLE)


class LoginView(TokenObtainPairView):
    pass


class RefreshTokenView(TokenRefreshView):
    pass
