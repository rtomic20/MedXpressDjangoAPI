from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.db.models import Prefetch, Q
from .serializers import (
    PacijentSerializer, LoginSerializer, InfirmarySerializer,
    DoktorSestraSerializer, DoktorSestraCreateSerializer,
    PacijentSerializer, DoktorSestraFullUpdateSerializer,
    InfirmaryUpdateSerializer,KorisnikProfileSerializer,ChangePasswordSerializer
)
from .models import Korisnik, MedicinskaSestra, Infirmary, Doktor, Pacijent,Conversation, Participant, Message, MessageStatus,Appointment, AppointmentAttendee
from django.http import JsonResponse


class RegisterPacijentAPIView(APIView):
    def post(self, request):
        serializer = PacijentSerializer(data=request.data)
        if serializer.is_valid():
            pacijent = serializer.save()
            return Response({'message': 'Pacijent uspješno registriran.'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class LoginAPIView(ListAPIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            korisnik = Korisnik.objects.get(
                korisnicko_ime=serializer.validated_data['korisnicko_ime']
            )

            response_data = {
                "id": korisnik.id,           
                "ime": korisnik.ime,
                "prezime": korisnik.prezime,
                "uloga": korisnik.uloga,
            }

            if korisnik.uloga == 'pacijent':
                try:
                    pac = Pacijent.objects.get(korisnik=korisnik)
                    response_data["pacijent_id"] = pac.pk   
                except Pacijent.DoesNotExist:
                    response_data["pacijent_id"] = None

            elif korisnik.uloga == 'doktor':
                try:
                    doc = Doktor.objects.get(korisnik=korisnik)
                    response_data["doktor_id"] = doc.pk
                except Doktor.DoesNotExist:
                    response_data["doktor_id"] = None

            elif korisnik.uloga == 'sestra':
                try:
                    sestra = MedicinskaSestra.objects.get(korisnik=korisnik)
                    response_data["sestra_id"] = sestra.pk
                    doktor = sestra.doktor.korisnik
                    response_data["doktor_ime"] = f"Dr. {doktor.ime} {doktor.prezime}"
                    response_data["doktor_id"] = sestra.doktor.pk
                except MedicinskaSestra.DoesNotExist:
                    response_data["sestra_id"] = None
                    response_data["doktor_ime"] = ""
                    response_data["doktor_id"] = None

            return Response(response_data, status=200)

        return Response(serializer.errors, status=400)

class KorisnikProfileAPI(APIView):
    def get_object(self, pk):
        try:
            return Korisnik.objects.get(pk=pk)
        except Korisnik.DoesNotExist:
            return None

    def get(self, request, pk):
        k = self.get_object(pk)
        if not k:
            return Response({"detail": "Korisnik nije pronađen."}, status=404)
        return Response(KorisnikProfileSerializer(k).data, status=200)

    def put(self, request, pk):
        k = self.get_object(pk)
        if not k:
            return Response({"detail": "Korisnik nije pronađen."}, status=404)
        s = KorisnikProfileSerializer(k, data=request.data)
        if s.is_valid():
            s.save()
            return Response({"message": "Profil ažuriran.", "profile": s.data}, status=200)
        return Response(s.errors, status=400)

    def patch(self, request, pk):
        k = self.get_object(pk)
        if not k:
            return Response({"detail": "Korisnik nije pronađen."}, status=404)
        s = KorisnikProfileSerializer(k, data=request.data, partial=True)
        if s.is_valid():
            s.save()
            return Response({"message": "Profil ažuriran.", "profile": s.data}, status=200)
        return Response(s.errors, status=400)


class ChangePasswordAPI(APIView):
    def post(self, request, pk):
        try:
            k = Korisnik.objects.get(pk=pk)
        except Korisnik.DoesNotExist:
            return Response({"detail": "Korisnik nije pronađen."}, status=404)

        s = ChangePasswordSerializer(data=request.data, context={"user": k})
        if not s.is_valid():
            return Response(s.errors, status=400)

        k.lozinka_hash = make_password(s.validated_data["new_password"])
        k.save(update_fields=["lozinka_hash"])
        return Response({"message": "Lozinka promijenjena."}, status=200)
    
class InfirmaryAPI(APIView):
    def get(self, request):
        infirmaries = Infirmary.objects.all()
        serializer = InfirmarySerializer(infirmaries, many=True)
        return JsonResponse(
            serializer.data,
            safe=False,
            json_dumps_params={'ensure_ascii': False}
        )

    def post(self, request):
        serializer = InfirmarySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PacientsViewAPI(APIView):
    def get(self, request):
        pacienti = Pacijent.objects.all()
        serializer = PacijentSerializer(pacienti, many=True)
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

class InfirmaryRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Infirmary.objects.all()
    serializer_class = InfirmaryUpdateSerializer

class ConversationsAPI(APIView):

    def get(self, request):
        qs = Conversation.objects.all().order_by('-updated_at')
        pid = request.GET.get('pacijent_id')
        did = request.GET.get('doktor_id')
        sid = request.GET.get('sestra_id')
        if pid:
            qs = qs.filter(pacijent_id=pid)
        if did:
            qs = qs.filter(doktor_id=did)
        if sid:
            qs = qs.filter(sestra_id=sid)

        data = []
        for c in qs.prefetch_related('participants__korisnik'):
            last_msg = c.messages.order_by('-created_at').first()
            data.append({
                "id": c.id,
                "title": c.title,
                "pacijent": c.pacijent_id,
                "doktor": c.doktor_id,
                "sestra": c.sestra_id,
                "created_at": c.created_at,
                "updated_at": c.updated_at,
                "participants": [
                    {
                        "id": p.id,
                        "korisnik_id": p.korisnik_id,
                        "korisnicko_ime": p.korisnik.korisnicko_ime,
                        "ime": p.korisnik.ime,           
                        "prezime": p.korisnik.prezime,
                        "role": p.role,
                        "joined_at": p.joined_at,
                        "last_read_at": p.last_read_at,
                    } for p in c.participants.all()
                ],
                "last_message": {
                    "id": last_msg.id,
                    "sender": last_msg.sender_id,
                    "body": last_msg.body,
                    "type": last_msg.type,
                    "created_at": last_msg.created_at,
                } if last_msg else None
            })
        return Response(data, status=200)

    def post(self, request):
        title = request.data.get("title", "")
        pacijent = request.data.get("pacijent")
        doktor = request.data.get("doktor")
        sestra = request.data.get("sestra")

        conv = Conversation.objects.create(
            title=title or "",
            pacijent_id=pacijent,
            doktor_id=doktor,
            sestra_id=sestra,
        )
        return Response({"id": conv.id}, status=201)


class ConversationParticipantsAPI(APIView):
    def get(self, request, conv_id):
        try:
            conv = Conversation.objects.get(pk=conv_id)
        except Conversation.DoesNotExist:
            return Response({"detail": "Conversation not found."}, status=404)

        parts = conv.participants.select_related('korisnik').all().order_by('id')

        data = [{
            "id": p.id,
            "korisnik_id": p.korisnik_id,
            "korisnicko_ime": p.korisnik.korisnicko_ime,
            "ime": p.korisnik.ime,               
            "prezime": p.korisnik.prezime,       
            "role": p.role,
            "joined_at": p.joined_at,
            "last_read_at": p.last_read_at,
        } for p in parts]

        return Response(data, status=200)

    def post(self, request, conv_id):
        try:
            conv = Conversation.objects.get(pk=conv_id)
        except Conversation.DoesNotExist:
            return Response({"detail": "Conversation not found."}, status=404)

        korisnik_id = request.data.get("korisnik_id")
        role = request.data.get("role")
        if not korisnik_id or role not in ("pacijent", "doktor", "sestra"):
            return Response({"detail": "korisnik_id i valjana role su obavezni."}, status=400)

        participant, created = Participant.objects.get_or_create(
            conversation=conv, korisnik_id=korisnik_id, defaults={"role": role}
        )
        if not created and participant.role != role:
            participant.role = role
            participant.save(update_fields=["role"])

        return Response({
            "id": participant.id,
            "korisnik_id": participant.korisnik_id,
            "role": participant.role
        }, status=201 if created else 200)


class ConversationMessagesAPI(APIView):

    def get(self, request, conv_id):
        try:
            conv = Conversation.objects.get(pk=conv_id)
        except Conversation.DoesNotExist:
            return Response({"detail": "Conversation not found."}, status=404)

        msgs = conv.messages.select_related('sender__korisnik').order_by('created_at')
        data = [{
            "id": m.id,
            "sender_participant": m.sender_id,
            "sender_korisnik_id": m.sender.korisnik_id,
            "sender_role": m.sender.role,
            "body": m.body,
            "type": m.type,
            "created_at": m.created_at,
            "edited_at": m.edited_at,
            "is_deleted": m.is_deleted,
        } for m in msgs]
        return Response(data, status=200)

    def post(self, request, conv_id):
        try:
            conv = Conversation.objects.get(pk=conv_id)
        except Conversation.DoesNotExist:
            return Response({"detail": "Conversation not found."}, status=404)

        sender_korisnik_id = request.data.get("sender_korisnik_id")
        body = (request.data.get("body") or "").strip()
        msg_type = request.data.get("type", "text")

        if not sender_korisnik_id or not body:
            return Response({"detail": "sender_korisnik_id i body su obavezni."}, status=400)

        try:
            sender_part = Participant.objects.get(conversation=conv, korisnik_id=sender_korisnik_id)
        except Participant.DoesNotExist:
            return Response({"detail": "Sender nije sudionik razgovora."}, status=400)

        msg = Message.objects.create(conversation=conv, sender=sender_part, body=body, type=msg_type)


        conv.updated_at = timezone.now()
        conv.save(update_fields=["updated_at"])

        others = conv.participants.exclude(id=sender_part.id)
        bulk = [MessageStatus(message=msg, participant=p, delivered_at=timezone.now()) for p in others]
        if bulk:
            MessageStatus.objects.bulk_create(bulk)

        return Response({
            "id": msg.id,
            "conversation": conv.id,
            "sender_participant": sender_part.id,
            "body": msg.body,
            "type": msg.type,
            "created_at": msg.created_at
        }, status=201)

class AppointmentsAPI(APIView):
   
    def get(self, request):
        qs = Appointment.objects.all().order_by('start_time')

        pid = request.GET.get('pacijent_id')
        did = request.GET.get('doktor_id')
        sid = request.GET.get('sestra_id')
        t_from = request.GET.get('from') 
        t_to = request.GET.get('to')     

        if pid:
            qs = qs.filter(pacijent_id=pid)
        if did:
            qs = qs.filter(doktor_id=did)
        if sid:
            qs = qs.filter(sestra_id=sid) 
        if t_from:
            qs = qs.filter(end_time__gte=t_from)
        if t_to:
            qs = qs.filter(start_time__lte=t_to)

        qs = qs.select_related('pacijent__korisnik', 'doktor__korisnik', 'sestra__korisnik', 'infirmary') \
               .prefetch_related('attendees__korisnik')

        data = []
        for a in qs:
            data.append({
                "id": a.id,
                "pacijent": a.pacijent_id,
                "doktor": a.doktor_id,
                "sestra": a.sestra_id,
                "infirmary": a.infirmary_id,
                "title": a.title,
                "note": a.note,
                "start_time": a.start_time,
                "end_time": a.end_time,
                "status": a.status,
                "priority": a.priority,
                "recurrence_rule": a.recurrence_rule,
                "created_at": a.created_at,
                "updated_at": a.updated_at,
                "doktor_ime": f"Dr. {a.doktor.korisnik.ime} {a.doktor.korisnik.prezime}" if a.doktor_id else None,
                "sestra_ime": f"{a.sestra.korisnik.ime} {a.sestra.korisnik.prezime}" if a.sestra_id else None, 
                "attendees": [{
                    "id": at.id,
                    "korisnik_id": at.korisnik_id,
                    "role": at.role,
                    "response_status": at.response_status,
                    "reminder_offset_min": at.reminder_offset_min,
                    "last_notified_at": at.last_notified_at,
                } for at in a.attendees.all()]
            })
        return Response(data, status=200)

    def post(self, request):
        body = request.data
        required = ["pacijent", "start_time", "end_time"]
        for f in required:
            if body.get(f) in (None, ""):
                return Response({"detail": f"{f} je obavezno."}, status=400)

        if body["start_time"] >= body["end_time"]:
            return Response({"detail": "start_time mora biti prije end_time."}, status=400)

        appt = Appointment.objects.create(
            pacijent_id=body["pacijent"],
            doktor_id=body.get("doktor"),
            sestra_id=body.get("sestra"),
            infirmary_id=body.get("infirmary"),
            title=body.get("title", ""),
            note=body.get("note", ""),
            start_time=body["start_time"],
            end_time=body["end_time"],
            status=body.get("status", "scheduled"),
            priority=body.get("priority", "normal"),
            recurrence_rule=body.get("recurrence_rule", "")
        )

        attendees_payload = body.get("attendees", [])
        attendees = [
            AppointmentAttendee(appointment=appt, korisnik_id=appt.pacijent.korisnik_id, role="pacijent", response_status="accepted")
        ]
        for it in attendees_payload:
            kid = it.get("korisnik_id")
            role = it.get("role")
            if kid and role in ("pacijent", "doktor", "sestra"):
                attendees.append(AppointmentAttendee(
                    appointment=appt,
                    korisnik_id=kid,
                    role=role,
                    response_status=it.get("response_status", "invited"),
                    reminder_offset_min=it.get("reminder_offset_min"),
                ))
        AppointmentAttendee.objects.bulk_create(attendees)

        return Response({"id": appt.id}, status=201)

class AppointmentDetailAPI(APIView):

    def get_object(self, pk):
        try:
            return Appointment.objects.select_related('pacijent__korisnik', 'doktor__korisnik', 'sestra__korisnik', 'infirmary') \
                                      .prefetch_related('attendees__korisnik').get(pk=pk)
        except Appointment.DoesNotExist:
            return None

    def get(self, request, pk):
        a = self.get_object(pk)
        if not a:
            return Response({"detail": "Appointment nije pronađen."}, status=404)

        return Response({
            "id": a.id,
            "pacijent": a.pacijent_id,
            "doktor": a.doktor_id,
            "sestra": a.sestra_id,
            "infirmary": a.infirmary_id,
            "title": a.title,
            "note": a.note,
            "start_time": a.start_time,
            "end_time": a.end_time,
            "status": a.status,
            "priority": a.priority,
            "recurrence_rule": a.recurrence_rule,
            "created_at": a.created_at,
            "updated_at": a.updated_at,
            "attendees": [{
                "id": at.id,
                "korisnik_id": at.korisnik_id,
                "role": at.role,
                "response_status": at.response_status,
                "reminder_offset_min": at.reminder_offset_min,
                "last_notified_at": at.last_notified_at,
            } for at in a.attendees.all()]
        }, status=200)

    def put(self, request, pk):
        a = self.get_object(pk)
        if not a:
            return Response({"detail": "Appointment nije pronađen."}, status=404)

        body = request.data
        for f in ["pacijent", "doktor", "sestra", "infirmary", "title", "note",
                  "status", "priority", "recurrence_rule"]:
            if f in body:
                setattr(a, f"{f}_id" if f in ["pacijent", "doktor", "sestra", "infirmary"] else f, body.get(f))

        if "start_time" in body:
            a.start_time = body["start_time"]
        if "end_time" in body:
            a.end_time = body["end_time"]
        if a.start_time and a.end_time and a.start_time >= a.end_time:
            return Response({"detail": "start_time mora biti prije end_time."}, status=400)

        a.save()
        return Response({"message": "Appointment ažuriran."}, status=200)

    def delete(self, request, pk):
        a = self.get_object(pk)
        if not a:
            return Response({"detail": "Appointment nije pronađen."}, status=404)
        a.delete()
        return Response(status=204)

class AppointmentAttendeesAPI(APIView):
   
    def post(self, request, id):
        try:
            appt = Appointment.objects.get(pk=id)
        except Appointment.DoesNotExist:
            return Response({"detail": "Appointment nije pronađen."}, status=404)

        kid = request.data.get("korisnik_id")
        role = request.data.get("role")
        if not kid or role not in ("pacijent", "doktor", "sestra"):
            return Response({"detail": "korisnik_id i valjana role su obavezni."}, status=400)

        att, created = AppointmentAttendee.objects.get_or_create(
            appointment=appt, korisnik_id=kid, defaults={
                "role": role,
                "response_status": request.data.get("response_status", "invited"),
                "reminder_offset_min": request.data.get("reminder_offset_min")
            }
        )
        if not created:
            changed = False
            if role and att.role != role:
                att.role = role
                changed = True
            rs = request.data.get("response_status")
            if rs and rs != att.response_status:
                att.response_status = rs
                changed = True
            if "reminder_offset_min" in request.data:
                att.reminder_offset_min = request.data.get("reminder_offset_min")
                changed = True
            if changed:
                att.save()

        return Response({
            "id": att.id,
            "korisnik_id": att.korisnik_id,
            "role": att.role,
            "response_status": att.response_status
        }, status=201 if created else 200)

    def delete(self, request, id, attendee_id):
        try:
            att = AppointmentAttendee.objects.get(pk=attendee_id, appointment_id=id)
        except AppointmentAttendee.DoesNotExist:
            return Response({"detail": "Attendee nije pronađen."}, status=404)
        att.delete()
        return Response(status=204)

class AppointmentRespondAPI(APIView):
   
    def post(self, request, id):
        kid = request.data.get("korisnik_id")
        rs = request.data.get("response_status")
        if not kid or rs not in ("accepted", "declined", "tentative", "attended", "no_show"):
            return Response({"detail": "korisnik_id i valjani response_status su obavezni."}, status=400)
        try:
            att = AppointmentAttendee.objects.get(appointment_id=id, korisnik_id=kid)
        except AppointmentAttendee.DoesNotExist:
            return Response({"detail": "Attendee nije pronađen za ovaj appointment."}, status=404)

        att.response_status = rs
        att.last_notified_at = timezone.now()
        att.save(update_fields=["response_status", "last_notified_at"])
        return Response({"message": "Status ažuriran."}, status=200)
