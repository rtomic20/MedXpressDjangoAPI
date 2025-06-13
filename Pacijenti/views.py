from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PacijentSerializer,LoginSerializer,InfirmarySerilazer,DoktorSestraSerializer
from .models import Korisnik, MedicinskaSestra,Infirmary,Doktor

class RegisterPacijentAPIView(APIView):
    def post(self, request):
        serializer = PacijentSerializer(data=request.data)
        if serializer.is_valid():
            pacijent = serializer.save()
            return Response({'message': 'Pacijent uspješno registriran.'}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors) 
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        h
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
    
class InfirmaryAPIView(APIView):
    class InfirmaryListAPIView(APIView):
        def get(self, request):
            infirmaries = Infirmary.objects.all()
            serializer = InfirmarySerilazer(infirmaries, many=True)
            return Response(serializer.data)

class DoktorSestraAPIView(APIView):
    def get(self, request):
        rezultat = []

        doktori = Doktor.objects.all()
        for doktor in doktori:
            sestre = MedicinskaSestra.objects.filter(doktor=doktor)
            sestre_imena = [
                f"{sestra.korisnik.ime} {sestra.korisnik.prezime}" for sestra in sestre
            ]

            rezultat.append({
                "doktor_ime": f"Dr. {doktor.korisnik.ime} {doktor.korisnik.prezime}",
                "medicinske_sestre": sestre_imena
            })

        serializer = DoktorSestraSerializer(rezultat, many=True)
        return Response(serializer.data)