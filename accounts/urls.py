from django.urls import path

from accounts.views import SignupView, LoginView, RefreshTokenView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('refresh_token/', RefreshTokenView.as_view(), name='refresh_token'),
]