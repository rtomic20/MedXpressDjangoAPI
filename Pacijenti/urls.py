from django.urls import path
from .views import RegisterPacijentAPIView,LoginAPIView,InfirmaryAPI,DoktorSestraAPIView,DoktorSestraCreateAPI,PacientsViewAPI,DoctorRetrieveUpdateDestroyAPIView,InfirmaryRetrieveUpdateDestroyAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', RegisterPacijentAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('pacients/',PacientsViewAPI.as_view(),name='Pacijenti'),
    path('infirmaries/',InfirmaryAPI.as_view(),name="infirmaries"),
    path('infirmaries/<int:pk>',InfirmaryRetrieveUpdateDestroyAPIView.as_view(),name='infirmary_detail'),
    path('doctors/',DoktorSestraAPIView.as_view(),name="doktor"),
    path('doktor_sestra_create/',DoktorSestraCreateAPI.as_view(),name='doctor_sestra_create'),
    path('doctors/<int:pk>', DoctorRetrieveUpdateDestroyAPIView.as_view(), name='doktor_detail'),
]