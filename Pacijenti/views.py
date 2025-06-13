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
    
class InfirmaryAPI(APIView):
    def get(self, request):
        infirmaries = Infirmary.objects.all()
        serializer = InfirmarySerilazer(infirmaries, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = InfirmarySerilazer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class DoktorSestraAPIView(APIView):
    def get(self, request):
        rezultat = []

        doktori = Doktor.objects.select_related('korisnik').all()
        for doktor in doktori:
            sestre = MedicinskaSestra.objects.filter(doktor=doktor).select_related('korisnik')
            if sestre.exists():
                sestra = sestre.first()
                rezultat.append({
                    "doktor_id":  doktor.korisnik.id,
                    "doktor_ime": f"Dr. {doktor.korisnik.ime} {doktor.korisnik.prezime}",
                    "sestra_id": sestra.korisnik.id,
                    "sestra_ime": f"{sestra.korisnik.ime} {sestra.korisnik.prezime}"
                })

        return Response(rezultat)
