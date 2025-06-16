from rest_framework import serializers
from .models import Korisnik, Pacijent,Infirmary,MedicinskaSestra
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
    

class InfirmarySerializer(serializers.ModelSerializer):
    doktor_ime = serializers.SerializerMethodField()
    sestra_ime = serializers.SerializerMethodField()

    class Meta:
        model = Infirmary
        fields = ['Infirmary_name', 'doktor', 'doktor_ime', 'medicinska_sestra', 'sestra_ime', 'long', 'lat']

    def get_doktor_ime(self, obj):
        return f"{obj.doktor.korisnik.ime} {obj.doktor.korisnik.prezime}"

    def get_sestra_ime(self, obj):
        return f"{obj.medicinska_sestra.korisnik.ime} {obj.medicinska_sestra.korisnik.prezime}"

    def create(self, validated_data):
        sestra_korisnik_id = self.initial_data.get("medicinska_sestra")

        try:
            sestra = MedicinskaSestra.objects.get(korisnik_id=sestra_korisnik_id)
            validated_data["medicinska_sestra"] = sestra
        except MedicinskaSestra.DoesNotExist:
            raise serializers.ValidationError({"medicinska_sestra": "Ne postoji sestra s tim korisnik_id."})

        return super().create(validated_data)



class DoktorSestraSerializer(serializers.Serializer):
    doktor_ime = serializers.CharField()
    medicinske_sestre = serializers.ListField(child=serializers.CharField())


