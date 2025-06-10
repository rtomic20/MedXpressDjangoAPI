from django.urls import path
from .views import RegisterPacijentAPIView,LoginAPIView,InfirmaryAPIView

urlpatterns = [
    path('register/', RegisterPacijentAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('infirmaries/',InfirmaryAPIView.as_view(),name="infirmaries"),
]