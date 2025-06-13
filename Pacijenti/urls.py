from django.urls import path
from .views import RegisterPacijentAPIView,LoginAPIView,InfirmaryAPI,DoktorSestraAPIView

urlpatterns = [
    path('register/', RegisterPacijentAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('infirmaries/',InfirmaryAPI.as_view(),name="infirmaries"),
    path('doctors/',DoktorSestraAPIView.as_view(),name="doktor")
]