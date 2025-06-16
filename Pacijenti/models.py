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
    
    long = models.DecimalField(max_digits=8, decimal_places=3) #longitute
    lat = models.DecimalField(max_digits=8, decimal_places=3)  #latitude 
    #Closest 45.3229931055812, 14.460150661377616
    
    