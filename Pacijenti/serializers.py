from rest_framework import serializers
from .models import Korisnik, Pacijent,Infirmary,MedicinskaSestra,Doktor,Conversation, Participant, Message, MessageStatus, Appointment, AppointmentAttendee
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
    
class SestraInfoSerializer(serializers.Serializer):
    korisnik_id = serializers.IntegerField(source='korisnik.id')
    ime = serializers.CharField(source='korisnik.ime')
    prezime = serializers.CharField(source='korisnik.prezime')
    
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
        fields = ['id','Infirmary_name', 'doktor', 'doktor_ime', 'medicinska_sestra', 'sestra_ime', 'long', 'lat']

    def get_doktor_ime(self, obj):
        return f"{obj.doktor.korisnik.ime} {obj.doktor.korisnik.prezime}"

    def get_sestra_ime(self, obj):
        return f"{obj.medicinska_sestra.korisnik.ime} {obj.medicinska_sestra.korisnik.prezime}"

    def create(self, validated_data):
        sestra_korisnik_id = self.initial_data.get("medicinska_sestra")
        doktor_id = self.initial_data.get("doktor")

        if sestra_korisnik_id:
            try:
                sestra = MedicinskaSestra.objects.get(
                    korisnik_id=sestra_korisnik_id,
                    doktor_id=doktor_id  
                )
                validated_data["medicinska_sestra"] = sestra
            except MedicinskaSestra.DoesNotExist:
                raise serializers.ValidationError({
                    "medicinska_sestra": "Ne postoji sestra s tim korisnik_id pod tim doktorom."
                })
        else:
            validated_data["medicinska_sestra"] = None
            
        return super().create(validated_data)

class DoktorSestraSerializer(serializers.Serializer):
    doktor_id = serializers.IntegerField(source='korisnik.id')
    ime = serializers.CharField(source='korisnik.ime')
    prezime = serializers.CharField(source='korisnik.prezime')
    email = serializers.EmailField(source='korisnik.email')
    specijalizacija = serializers.CharField()
    razina_specijalizacije = serializers.CharField()
    sestra = serializers.SerializerMethodField()

    def get_sestra(self, obj):
        sestra = obj.sestre.first() 
        if sestra:
            return {
                "medicinskasestra_id": sestra.korisnik_id,
                "ime": sestra.korisnik.ime,
                "prezime": sestra.korisnik.prezime,
                "radno_iskustvo": sestra.radno_iskustvo,
                "specializirane_tehnike": sestra.specializirane_tehnike
            }
        else:
            return None
     
class SestraNestedSerializer(serializers.Serializer):
    ime = serializers.CharField()
    prezime = serializers.CharField()
    email = serializers.EmailField()
    korisnicko_ime = serializers.CharField()
    lozinka = serializers.CharField(write_only=True)
    radno_iskustvo = serializers.CharField()
    specializirane_tehnike = serializers.CharField()

class DoktorSestraCreateSerializer(serializers.Serializer):

    ime = serializers.CharField()
    prezime = serializers.CharField()
    email = serializers.EmailField()
    korisnicko_ime = serializers.CharField()
    lozinka = serializers.CharField(write_only=True)
    specijalizacija = serializers.CharField()
    razina_specijalizacije = serializers.CharField()

    sestra = SestraNestedSerializer()

    def create(self, validated_data):
        sestra_data = validated_data.pop('sestra')
        lozinka = validated_data.pop('lozinka')

        korisnik_doktor = Korisnik.objects.create(
            ime=validated_data['ime'],
            prezime=validated_data['prezime'],
            email=validated_data['email'],
            korisnicko_ime=validated_data['korisnicko_ime'],
            lozinka_hash=make_password(lozinka),
            uloga='doktor'
        )

        doktor = Doktor.objects.create(
            korisnik=korisnik_doktor,
            specijalizacija=validated_data['specijalizacija'],
            razina_specijalizacije=validated_data['razina_specijalizacije']
        )
        
        korisnik_sestra = Korisnik.objects.create(
            ime=sestra_data['ime'],
            prezime=sestra_data['prezime'],
            email=sestra_data['email'],
            korisnicko_ime=sestra_data['korisnicko_ime'],
            lozinka_hash=make_password(sestra_data['lozinka']),
            uloga='sestra'
        )

        MedicinskaSestra.objects.create(
            korisnik=korisnik_sestra,
            doktor=doktor,
            radno_iskustvo=sestra_data['radno_iskustvo'],
            specializirane_tehnike=sestra_data['specializirane_tehnike']
        )

        return doktor

class KorisnikSerializer(serializers.ModelSerializer):
    class Meta:
        model = Korisnik
        fields = ['ime', 'prezime', 'email', 'korisnicko_ime']

class PacijentSerializer(serializers.ModelSerializer):
    korisnik = KorisnikSerializer()  
    
    class Meta:
        model = Pacijent
        fields = ['korisnik', 'povijest_bolesti', 'simptomi_bolesti', 'primljena_cijepiva']
class SestraUpdateSerializer(serializers.Serializer):
    ime = serializers.CharField()
    prezime = serializers.CharField()
    email = serializers.EmailField()
    radno_iskustvo = serializers.CharField()
    specializirane_tehnike = serializers.CharField()

class DoktorSestraFullUpdateSerializer(serializers.Serializer):
    ime = serializers.CharField(source='korisnik.ime')
    prezime = serializers.CharField(source='korisnik.prezime')
    email = serializers.EmailField(source='korisnik.email')
    specijalizacija = serializers.CharField()
    razina_specijalizacije = serializers.CharField()

    sestra = serializers.DictField()

    def update(self, instance, validated_data):
        korisnik_data = validated_data.pop('korisnik')
        instance.korisnik.ime = korisnik_data.get('ime', instance.korisnik.ime)
        instance.korisnik.prezime = korisnik_data.get('prezime', instance.korisnik.prezime)
        instance.korisnik.email = korisnik_data.get('email', instance.korisnik.email)
        instance.korisnik.save()

        instance.specijalizacija = validated_data.get('specijalizacija', instance.specijalizacija)
        instance.razina_specijalizacije = validated_data.get('razina_specijalizacije', instance.razina_specijalizacije)
        instance.save()

        sestra_obj = instance.sestre.first()
        if sestra_obj and 'sestra' in validated_data:
            sestra_data = validated_data['sestra']
            sestra_obj.korisnik.ime = sestra_data.get('ime', sestra_obj.korisnik.ime)
            sestra_obj.korisnik.prezime = sestra_data.get('prezime', sestra_obj.korisnik.prezime)
            sestra_obj.radno_iskustvo = sestra_data.get('radno_iskustvo', sestra_obj.radno_iskustvo)
            sestra_obj.specializirane_tehnike = sestra_data.get('specializirane_tehnike', sestra_obj.specializirane_tehnike)
            sestra_obj.korisnik.save()
            sestra_obj.save()

        return instance

class InfirmaryUpdateSerializer(serializers.Serializer):
    Infirmary_name = serializers.CharField(required=False)
    doktor = serializers.PrimaryKeyRelatedField(read_only=True)
    sestra = serializers.PrimaryKeyRelatedField(read_only=True)
    lat = serializers.FloatField(required=False)
    long = serializers.FloatField(required=False)

    def update(self, instance, validated_data):
        instance.Infirmary_name = validated_data.get('Infirmary_name', instance.Infirmary_name)
        instance.lat = validated_data.get('lat', instance.lat)
        instance.long = validated_data.get('long', instance.long)

        if 'doktor' in validated_data:
            try:
                doktor = Doktor.objects.get(id=validated_data['doktor'])
                instance.doktor = doktor
            except Doktor.DoesNotExist:
                raise serializers.ValidationError({"doktor": "Doktor s ovim ID-em ne postoji."})

        if 'medicinska_sestra' in validated_data:
            try:
                sestra = MedicinskaSestra.objects.get(korisnik_id=validated_data['medicinska_sestra'])
                instance.medicinska_sestra = sestra
            except MedicinskaSestra.DoesNotExist:
                raise serializers.ValidationError({"medicinska_sestra": "Sestra s ovim korisnik_id ne postoji."})

        instance.save()
        return instance

class ParticipantSerializer(serializers.ModelSerializer):
    korisnik_id = serializers.IntegerField(source='korisnik.id', read_only=True)
    korisnicko_ime = serializers.CharField(source='korisnik.korisnicko_ime', read_only=True)

    class Meta:
        model = Participant
        fields = ['id', 'korisnik_id', 'korisnicko_ime', 'role', 'joined_at', 'last_read_at']

class MessageSerializer(serializers.ModelSerializer):
    sender_role = serializers.CharField(source='sender.role', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'sender_role', 'body', 'type', 'created_at', 'edited_at', 'is_deleted']
        read_only_fields = ['created_at', 'edited_at', 'sender_role']

class MessageStatusSerializer(serializers.ModelSerializer):
    participant_id = serializers.IntegerField(source='participant.id', read_only=True)

    class Meta:
        model = MessageStatus
        fields = ['id', 'message', 'participant_id', 'delivered_at', 'read_at']

class ConversationSerializer(serializers.ModelSerializer):
    participants = ParticipantSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'title', 'pacijent', 'doktor', 'sestra', 'created_at', 'updated_at', 'participants', 'last_message']
        read_only_fields = ['created_at', 'updated_at']

    def get_last_message(self, obj):
        msg = obj.messages.order_by('-created_at').first()
        return MessageSerializer(msg).data if msg else None
    
class AppointmentAttendeeSerializer(serializers.ModelSerializer):
    korisnik_id = serializers.IntegerField(source='korisnik.id', read_only=True)
    korisnicko_ime = serializers.CharField(source='korisnik.korisnicko_ime', read_only=True)

    class Meta:
        model = AppointmentAttendee
        fields = ['id', 'appointment', 'korisnik_id', 'korisnicko_ime', 'role', 'response_status', 'reminder_offset_min', 'last_notified_at']

class AppointmentSerializer(serializers.ModelSerializer):
    attendees = AppointmentAttendeeSerializer(many=True, read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'pacijent', 'doktor', 'sestra', 'infirmary',
            'title', 'note', 'start_time', 'end_time', 'status', 'priority',
            'recurrence_rule', 'created_at', 'updated_at', 'attendees'
        ]
        read_only_fields = ['created_at', 'updated_at']