from django.db import models
import random

class Korisnik(models.Model):
    ULOGE = (
        ('pacijent', 'Pacijent'),
        ('doktor', 'Doktor'),
        ('sestra', 'Medicinska sestra'),
    )
    ime = models.CharField(max_length=100)
    prezime = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    korisnicko_ime = models.CharField(max_length=100, unique=True)
    lozinka_hash = models.TextField()
    uloga = models.CharField(max_length=20, choices=ULOGE, default='pacijent')

class Pacijent(models.Model):
    korisnik = models.OneToOneField(Korisnik, on_delete=models.CASCADE, primary_key=True)

    povijest_bolesti = models.TextField(blank=True)
    simptomi_bolesti = models.TextField(blank=True)
    primljena_cijepiva = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.povijest_bolesti:
            self.povijest_bolesti = random.choice([
                "Astma u djetinjstvu", "Nema značajne povijesti", "Dijabetes tip 2", "Hipertenzija"
            ])
        if not self.simptomi_bolesti:
            self.simptomi_bolesti = random.choice([
                "Kašalj i glavobolja", "Nema simptoma trenutno", "Mučnina i bolovi u trbuhu", "Blaga vrtoglavica"
            ])
        if not self.primljena_cijepiva:
            self.primljena_cijepiva = random.choice([
                "Pfizer, Tetanus", "Moderna, Hepatitis B", "AstraZeneca", "COVID-19, HPV", "Nema podataka"
            ])
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pacijent: {self.korisnik.korisnicko_ime}"

class Doktor(models.Model):
    korisnik = models.OneToOneField(Korisnik, on_delete=models.CASCADE, primary_key=True)

    specijalizacija = models.CharField(max_length=100)
    razina_specijalizacije = models.CharField(max_length=100)

    def __str__(self):
        return f"Dr. {self.korisnik.ime} {self.korisnik.prezime} ({self.specijalizacija})"


class MedicinskaSestra(models.Model):
    korisnik = models.OneToOneField(Korisnik, on_delete=models.CASCADE, primary_key=True)
    doktor = models.ForeignKey(Doktor, on_delete=models.CASCADE, related_name="sestre")

    radno_iskustvo = models.CharField(max_length=100)
    specializirane_tehnike = models.TextField()

    def __str__(self):
        return f"Sestra {self.korisnik.ime} {self.korisnik.prezime}"

class Infirmary (models.Model):
    Infirmary_name=models.CharField(max_length=200,blank=True,null=True)
    doktor=models.ForeignKey(Doktor,on_delete=models.CASCADE,related_name="doctor")
    medicinska_sestra=models.ForeignKey(MedicinskaSestra,on_delete=models.CASCADE,related_name="sestre")
    
    long = models.DecimalField(max_digits=8, decimal_places=3) 
    lat = models.DecimalField(max_digits=8, decimal_places=3) 

class Conversation(models.Model):
    title = models.CharField(max_length=255, blank=True, default="")
    pacijent = models.ForeignKey(Pacijent, null=True, blank=True, on_delete=models.SET_NULL, related_name="conversations")
    doktor = models.ForeignKey(Doktor, null=True, blank=True, on_delete=models.SET_NULL, related_name="conversations")
    sestra = models.ForeignKey(MedicinskaSestra, null=True, blank=True, on_delete=models.SET_NULL, related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["updated_at"]),
            models.Index(fields=["pacijent"]),
            models.Index(fields=["doktor"]),
            models.Index(fields=["sestra"]),
        ]

    def __str__(self):
        return f"Conversation {self.pk}"


class Participant(models.Model):
    ROLE = (
        ("pacijent", "Pacijent"),
        ("doktor", "Doktor"),
        ("sestra", "Medicinska sestra"),
    )
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="participants")
    korisnik = models.ForeignKey(Korisnik, on_delete=models.CASCADE, related_name="chat_participations")
    role = models.CharField(max_length=16, choices=ROLE)
    joined_at = models.DateTimeField(auto_now_add=True)
    last_read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("conversation", "korisnik")
        indexes = [
            models.Index(fields=["conversation", "korisnik"]),
            models.Index(fields=["role"]),
        ]

    def __str__(self):
        return f"{self.korisnik.korisnicko_ime} in {self.conversation_id}"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(Participant, on_delete=models.PROTECT, related_name="sent_messages")
    body = models.TextField(blank=True, default="")
    type = models.CharField(max_length=32, default="text") 
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["conversation", "created_at"]),
        ]

    def __str__(self):
        return f"Msg {self.pk} conv {self.conversation_id}"

class MessageStatus(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="statuses")
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name="message_statuses")
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("message", "participant")
        indexes = [
            models.Index(fields=["participant", "message"]),
        ]

    def __str__(self):
        return f"Status msg {self.message_id} part {self.participant_id}"

class Appointment(models.Model):
    STATUS = (
        ("scheduled", "Zakazano"),
        ("confirmed", "Potvrđeno"),
        ("cancelled", "Otkazano"),
        ("completed", "Završeno"),
        ("no_show", "Nije došao"),
    )
    pacijent = models.ForeignKey(Pacijent, on_delete=models.CASCADE, related_name="appointments")
   
    doktor = models.ForeignKey(Doktor, null=True, blank=True, on_delete=models.SET_NULL, related_name="appointments")
    sestra = models.ForeignKey(MedicinskaSestra, null=True, blank=True, on_delete=models.SET_NULL, related_name="appointments")

    infirmary = models.ForeignKey(Infirmary, null=True, blank=True, on_delete=models.SET_NULL, related_name="appointments")
    title = models.CharField(max_length=200, blank=True, default="")
    note = models.TextField(blank=True, default="")

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=16, choices=STATUS, default="scheduled")
    priority = models.CharField(max_length=16, default="normal")  

    recurrence_rule = models.CharField(max_length=255, blank=True, default="")  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["start_time"]),
            models.Index(fields=["end_time"]),
            models.Index(fields=["status"]),
            models.Index(fields=["pacijent"]),
            models.Index(fields=["doktor"]),
            models.Index(fields=["sestra"]),
        ]

    def __str__(self):
        return f"Appt {self.pk} {self.start_time}"

class AppointmentAttendee(models.Model):
    ROLE = (
        ("pacijent", "Pacijent"),
        ("doktor", "Doktor"),
        ("sestra", "Medicinska sestra"),
    )
    RESP = (
        ("invited", "Pozvan"),
        ("accepted", "Prihvatio"),
        ("declined", "Odbio"),
        ("tentative", "Možda"),
        ("attended", "Prisustvovao"),
        ("no_show", "Nije došao"),
    )

    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name="attendees")
    korisnik = models.ForeignKey(Korisnik, on_delete=models.CASCADE, related_name="appointment_participations")
    role = models.CharField(max_length=16, choices=ROLE)
    response_status = models.CharField(max_length=16, choices=RESP, default="invited")
    reminder_offset_min = models.IntegerField(null=True, blank=True)  
    last_notified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("appointment", "korisnik")
        indexes = [
            models.Index(fields=["appointment", "korisnik"]),
            models.Index(fields=["role"]),
            models.Index(fields=["response_status"]),
        ]

    def __str__(self):
        return f"Attendee {self.korisnik.korisnicko_ime} appt {self.appointment_id}"
   
    