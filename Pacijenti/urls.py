from django.urls import path
from .views import RegisterPacijentAPIView,LoginAPIView

urlpatterns = [
    path('register/', RegisterPacijentAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
]