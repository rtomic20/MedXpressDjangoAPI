from django.urls import path
from .views import RegisterPacijentAPIView,LoginAPIView,InfirmaryAPI,DoktorSestraAPIView,DoktorSestraCreateAPI,PacientsViewAPI,DoctorRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('register/', RegisterPacijentAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('infirmaries/',InfirmaryAPI.as_view(),name="infirmaries"),
    path('doctors/',DoktorSestraAPIView.as_view(),name="doktor"),
    path('doktor_sestra_create/',DoktorSestraCreateAPI.as_view(),name='doctor_sestra_create'),
    path('pacients/',PacientsViewAPI.as_view(),name='Pacijenti'),
    path('doctors/<int:pk>', DoctorRetrieveUpdateDestroyAPIView.as_view(), name='doktor_detail'),
]