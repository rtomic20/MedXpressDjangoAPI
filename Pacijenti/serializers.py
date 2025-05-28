from rest_framework import serializers
from .models import Korisnik, Pacijent
from django.contrib.auth.hashers import make_password,check_password

class KorisnikSerializer(serializers.ModelSerializer):
    class Meta:
        model = Korisnik
        fields = ['ime', 'prezime', 'email', 'korisnicko_ime', 'lozinka_hash']

    def validate_lozinka_hash(self, value):
        return make_password(value)

class PacijentSerializer(serializers.ModelSerializer):
    korisnik = KorisnikSerializer()

    class Meta:
        model = Pacijent
        fields = ['korisnik']

    def create(self, validated_data):
        korisnik_data = validated_data.pop('korisnik')
        korisnik = Korisnik.objects.create(**korisnik_data)
        pacijent = Pacijent.objects.create(korisnik=korisnik)
        return pacijent
    
class LoginSerializer(serializers.Serializer):
    korisnicko_ime = serializers.CharField()
    lozinka = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            korisnik = Korisnik.objects.get(korisnicko_ime=data['korisnicko_ime'])
        except Korisnik.DoesNotExist:
            raise serializers.ValidationError("Korisnik ne postoji.")

        if not check_password(data['lozinka'], korisnik.lozinka_hash):
            raise serializers.ValidationError("Pogrešna lozinka.")

        return {
            "korisnicko_ime": korisnik.korisnicko_ime,  
            "ime": korisnik.ime,
            "prezime": korisnik.prezime,
            "uloga": korisnik.uloga,
        }
