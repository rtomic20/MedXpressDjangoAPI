from django.urls import path
from .views import (
    RegisterPacijentAPIView,
    LoginAPIView,
    InfirmaryAPI,
    DoktorSestraAPIView,
    DoktorSestraCreateAPI,
    PacientsViewAPI,
    DoctorRetrieveUpdateDestroyAPIView,
    InfirmaryRetrieveUpdateDestroyAPIView,
    ChangePasswordAPI,
    KorisnikProfileAPI,

    ConversationsAPI,
    ConversationParticipantsAPI,
    ConversationMessagesAPI,

    AppointmentsAPI,
    AppointmentDetailAPI,
    AppointmentAttendeesAPI,
    AppointmentRespondAPI,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', RegisterPacijentAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('korisnici/<int:pk>/', KorisnikProfileAPI.as_view(), name='korisnik-profile'),
    path('korisnici/<int:pk>/change-password', ChangePasswordAPI.as_view(), name='korisnik-change-password'),
    
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('pacients/',PacientsViewAPI.as_view(),name='Pacijenti'),
    path('infirmaries/',InfirmaryAPI.as_view(),name="infirmaries"),
    path('infirmaries/<int:pk>',InfirmaryRetrieveUpdateDestroyAPIView.as_view(),name='infirmary_detail'),
    path('doctors/',DoktorSestraAPIView.as_view(),name="doktor"),
    path('doktor_sestra_create/',DoktorSestraCreateAPI.as_view(),name='doctor_sestra_create'),
    path('doctors/<int:pk>', DoctorRetrieveUpdateDestroyAPIView.as_view(), name='doktor_detail'),
    
    path("conversations/", ConversationsAPI.as_view(), name="conversation_list_create"),
    path("conversations/<int:conv_id>/participants/", ConversationParticipantsAPI.as_view(), name="conversation_participants"),
    path("conversations/<int:conv_id>/messages/", ConversationMessagesAPI.as_view(), name="conversation_messages"),
    
    path("appointments/", AppointmentsAPI.as_view(), name="appointment_list_create"),
    path("appointments/<int:pk>/", AppointmentDetailAPI.as_view(), name="appointment_detail"),
    path("appointments/<int:id>/attendees/", AppointmentAttendeesAPI.as_view(), name="appointment_attendees"),
    path("appointments/<int:id>/attendees/<int:attendee_id>/", AppointmentAttendeesAPI.as_view(), name="appointment_attendee_delete"),
    path("appointments/<int:id>/respond/", AppointmentRespondAPI.as_view(), name="appointment_respond"),
]