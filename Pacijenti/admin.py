from django.contrib import admin
from django.contrib.auth.hashers import make_password
from .models import Korisnik, Doktor, MedicinskaSestra, Pacijent,Infirmary

class KorisnikAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not obj.pk or 'lozinka_hash' in form.changed_data:
            obj.lozinka_hash = make_password(obj.lozinka_hash)
        super().save_model(request, obj, form, change)

admin.site.register(Korisnik, KorisnikAdmin)
admin.site.register(Doktor)
admin.site.register(MedicinskaSestra)
admin.site.register(Pacijent)
admin.site.register(Infirmary)
