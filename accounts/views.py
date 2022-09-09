from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken


from accounts.serializers import SignupSerializer, TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


class SignupView(APIView):
    serializer_class = SignupSerializer
    permission_classes = []

    def post(self, request):
        serializer_data = self.serializer_class(data=request.data)
        if serializer_data.is_valid():
            serializer_data.save()
            # TODO: replace with redirect
            token_serializer_data = TokenObtainPairSerializer(data = serializer_data.validated_data)
            if token_serializer_data.is_valid():
                return Response(data = token_serializer_data.validated_data, status=status.HTTP_200_OK)

        return Response(data= serializer_data.errors, status= status.HTTP_406_NOT_ACCEPTABLE)


class LoginView(TokenObtainPairView):
    pass


class RefreshTokenView(TokenRefreshView):
    pass


class LogoutView(APIView):
    serializer_class = None
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        try:
            refresh_token = request.data['refresh_token']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)

        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)