from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PacijentSerializer,LoginSerializer,InfirmarySerializer,DoktorSestraSerializer,DoktorSestraCreateSerializer,PacijentSerializer,DoktorSestraFullUpdateSerializer
from .models import Korisnik, MedicinskaSestra,Infirmary,Doktor,Pacijent

class RegisterPacijentAPIView(APIView):
    def post(self, request):
        serializer = PacijentSerializer(data=request.data)
        if serializer.is_valid():
            pacijent = serializer.save()
            return Response({'message': 'Pacijent uspješno registriran.'}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors) 
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class LoginAPIView(ListAPIView):
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
        serializer = InfirmarySerializer(infirmaries, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = InfirmarySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        print("Greške:", serializer.errors)
        return Response(serializer.errors, status=400)

class DoktorSestraAPIView(APIView):
   def get(self, request):
        doktori = Doktor.objects.select_related('korisnik').prefetch_related('sestre__korisnik').all()
        
        serializer = DoktorSestraSerializer(doktori, many=True)
        
        return Response(serializer.data)

class DoktorSestraCreateAPI(APIView):
    def post(self, request):
        serializer = DoktorSestraCreateSerializer(data=request.data)
        if serializer.is_valid():
            doktor = serializer.save()
            return Response({
                'message': 'Doktor i sestre uspješno dodani.',
                'doktor_id': doktor.pk,
                'doktor_ime': f"Dr. {doktor.korisnik.ime} {doktor.korisnik.prezime}"
            }, status=status.HTTP_201_CREATED)
        else:
            print("Greške:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PacientsViewAPI(APIView):
    def get(self,request):
        pacienti=Pacijent.objects.all()
        serializer=PacijentSerializer(pacienti,many=True)
        return Response(serializer.data)


class DoctorRetrieveUpdateDestroyAPIView(APIView):
    def get_object(self, pk):
        try:
            return Doktor.objects.select_related('korisnik').prefetch_related('sestre__korisnik').get(pk=pk)
        except Doktor.DoesNotExist:
            return None

    def get(self, request, pk):
        doktor = self.get_object(pk)
        if not doktor:
            return Response({"error": "Doktor nije pronađen."}, status=status.HTTP_404_NOT_FOUND)

        serializer = DoktorSestraSerializer(doktor)
        return Response(serializer.data)

    def put(self, request, pk):
        doktor = self.get_object(pk)
        if not doktor:
            return Response({"error": "Doktor nije pronađen."}, status=status.HTTP_404_NOT_FOUND)

        from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PacijentSerializer,LoginSerializer,InfirmarySerializer,DoktorSestraSerializer,DoktorSestraCreateSerializer,PacijentSerializer,DoktorSestraFullUpdateSerializer
from .models import Korisnik, MedicinskaSestra,Infirmary,Doktor,Pacijent

class RegisterPacijentAPIView(APIView):
    def post(self, request):
        serializer = PacijentSerializer(data=request.data)
        if serializer.is_valid():
            pacijent = serializer.save()
            return Response({'message': 'Pacijent uspješno registriran.'}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors) 
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class LoginAPIView(ListAPIView):
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
        serializer = InfirmarySerializer(infirmaries, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = InfirmarySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        print("Greške:", serializer.errors)
        return Response(serializer.errors, status=400)

class DoktorSestraAPIView(APIView):
   def get(self, request):
        doktori = Doktor.objects.select_related('korisnik').prefetch_related('sestre__korisnik').all()
        
        serializer = DoktorSestraSerializer(doktori, many=True)
        
        return Response(serializer.data)

class DoktorSestraCreateAPI(APIView):
    def post(self, request):
        serializer = DoktorSestraCreateSerializer(data=request.data)
        if serializer.is_valid():
            doktor = serializer.save()
            return Response({
                'message': 'Doktor i sestre uspješno dodani.',
                'doktor_id': doktor.pk,
                'doktor_ime': f"Dr. {doktor.korisnik.ime} {doktor.korisnik.prezime}"
            }, status=status.HTTP_201_CREATED)
        else:
            print("Greške:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PacientsViewAPI(APIView):
    def get(self,request):
        pacienti=Pacijent.objects.all()
        serializer=PacijentSerializer(pacienti,many=True)
        return Response(serializer.data)


class DoctorRetrieveUpdateDestroyAPIView(APIView):
    def get_object(self, pk):
        try:
            return Doktor.objects.select_related('korisnik').prefetch_related('sestre__korisnik').get(pk=pk)
        except Doktor.DoesNotExist:
            return None

    def get(self, request, pk):
        doktor = self.get_object(pk)
        if not doktor:
            return Response({"error": "Doktor nije pronađen."}, status=status.HTTP_404_NOT_FOUND)

        serializer = DoktorSestraSerializer(doktor)
        return Response(serializer.data)

    def put(self, request, pk):
        doktor = self.get_object(pk)
        if not doktor:
            return Response({"error": "Doktor nije pronađen."}, status=status.HTTP_404_NOT_FOUND)

        serializer = DoktorSestraFullUpdateSerializer(doktor, data=request.data)
        if serializer.is_valid():
            serializer.update(doktor, serializer.validated_data)

            return Response({"message": "Doktor i sestra su uspješno ažurirani."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk):
        doktor = self.get_object(pk)
        if not doktor:
            return Response({"error": "Doktor nije pronađen."}, status=status.HTTP_404_NOT_FOUND)

        doktor.delete()
        return Response({"message": "Doktor je obrisan."}, status=status.HTTP_204_NO_CONTENT)


        if serializer.is_valid():
            serializer.update(doktor, serializer.validated_data)

            return Response({"message": "Doktor i sestra su uspješno ažurirani."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk):
        doktor = self.get_object(pk)
        if not doktor:
            return Response({"error": "Doktor nije pronađen."}, status=status.HTTP_404_NOT_FOUND)

        doktor.delete()
        return Response({"message": "Doktor je obrisan."}, status=status.HTTP_204_NO_CONTENT)

