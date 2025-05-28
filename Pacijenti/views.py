from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PacijentSerializer,LoginSerializer
from .models import Korisnik, MedicinskaSestra

class RegisterPacijentAPIView(APIView):
    def post(self, request):
        serializer = PacijentSerializer(data=request.data)
        if serializer.is_valid():
            pacijent = serializer.save()
            return Response({'message': 'Pacijent uspješno registriran.'}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors) 
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            korisnik = Korisnik.objects.get(korisnicko_ime=serializer.validated_data['korisnicko_ime'])
            response_data = {
                "ime": korisnik.ime,
                "prezime": korisnik.prezime,
                "uloga": korisnik.uloga,
            }

            if korisnik.uloga == 'sestra':
                try:
                    sestra = MedicinskaSestra.objects.get(korisnik=korisnik)
                    doktor = sestra.doktor.korisnik
                    response_data["doktor_ime"] = f"Dr. {doktor.ime} {doktor.prezime}"
                except MedicinskaSestra.DoesNotExist:
                    response_data["doktor_ime"] = ""

            return Response(response_data, status=200)

        return Response(serializer.errors, status=400)