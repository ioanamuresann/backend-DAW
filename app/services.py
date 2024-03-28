from datetime import timedelta
import uuid
from flask import jsonify
from app.models import Destinatie, Rezervare, User
from app import db
from sqlalchemy import extract

class UserService:
    @staticmethod
    def create_user(nume, prenume, email, parola, rol):
        id = str(uuid.uuid4())
        user = User(id=id, nume=nume, prenume=prenume, email=email, parola=parola, rol=rol)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_user_by_email(email):
        return User.query.filter_by(email=email).first()
    
class DestinatieService:
    @staticmethod
    def get_destinatii():
        destinatii = Destinatie.query.all()
        serialized_destinatii = []
        for destinatie in destinatii:
            serialized_destinatii.append({
                'id': destinatie.id,
                'titlu': destinatie.titlu,
                'descriere': destinatie.descriere,
                'locatie': destinatie.locatie,
                'pret_per_noapte': destinatie.pret_per_noapte,
                'numar_locuri': destinatie.numar_locuri,
                'imagine': destinatie.imagine,
                'procent_reducere': destinatie.procent_reducere
            })
        return jsonify(serialized_destinatii), 200

    @staticmethod
    def create_destinatie(data):
        titlu = data.get('titlu')
        descriere = data.get('descriere')
        locatie = data.get('locatie')
        pret_per_noapte = data.get('pret_per_noapte')
        numar_locuri = data.get('numar_locuri')
        imagine = data.get('imagine')
        procent_reducere = data.get('procent_reducere')

        if not all([titlu, descriere, locatie, pret_per_noapte, numar_locuri, imagine, procent_reducere]):
            return jsonify({'message': 'Toate câmpurile sunt obligatorii!'}), 400

        destinatie = Destinatie(titlu=titlu, descriere=descriere, locatie=locatie, pret_per_noapte=pret_per_noapte, numar_locuri=numar_locuri, imagine=imagine, procent_reducere=procent_reducere)
        db.session.add(destinatie)
        db.session.commit()
        return jsonify({'message': 'Destinație adăugată cu succes!', 'destinatie_id': destinatie.id}), 201

    @staticmethod
    def update_destinatie(destinatie_id, data):
        destinatie = Destinatie.query.get(destinatie_id)
        if not destinatie:
            return jsonify({'message': 'Destinație inexistentă!'}), 404

        destinatie.titlu = data.get('titlu', destinatie.titlu)
        destinatie.descriere = data.get('descriere', destinatie.descriere)
        destinatie.locatie = data.get('locatie', destinatie.locatie)
        destinatie.pret_per_noapte = data.get('pret_per_noapte', destinatie.pret_per_noapte)
        destinatie.numar_locuri = data.get('numar_locuri', destinatie.numar_locuri)
        destinatie.imagine = data.get('imagine', destinatie.imagine)
        destinatie.procent_reducere = data.get('procent_reducere', destinatie.procent_reducere)

        db.session.commit()
        return jsonify({'message': 'Destinație actualizată cu succes!'}), 200

    @staticmethod
    def delete_destinatie(destinatie_id):
        destinatie = Destinatie.query.get(destinatie_id)
        if not destinatie:
            return jsonify({'message': 'Destinație inexistentă!'}), 404

        db.session.delete(destinatie)
        db.session.commit()
        return jsonify({'message': 'Destinație ștearsă cu succes!'}), 200
    

class RezervareService:
    @staticmethod
    def create_rezervare(destinatie_id, user_id, data_inceput, data_sfarsit):
        destinatie = Destinatie.query.get(destinatie_id)
        if not destinatie:
            return jsonify({'message': 'Destinație inexistentă!'}), 404

        numar_zile = (data_sfarsit - data_inceput).days + 1
        numar_locuri_pe_zi = destinatie.numar_locuri

        for zi in range(numar_zile):
            data_curenta = data_inceput + timedelta(days=zi)
            rezervari_existente_pe_zi = Rezervare.query.filter(
                Rezervare.destinatie_id == destinatie_id,
                Rezervare.data_inceput <= data_curenta,
                Rezervare.data_sfarsit >= data_curenta
            ).count()

            if rezervari_existente_pe_zi >= numar_locuri_pe_zi:
                return jsonify({'message': f'Nu sunt suficiente locuri disponibile pe data de {data_curenta}!'}), 400

        cost_total = numar_zile * destinatie.pret_per_noapte * (1 - destinatie.procent_reducere / 100)

        rezervare = Rezervare(
            destinatie_id=destinatie_id,
            user_id=user_id,
            data_inceput=data_inceput,
            data_sfarsit=data_sfarsit,
            cost_total=cost_total
        )

        db.session.add(rezervare)
        db.session.commit()
        
        return jsonify({'message': 'Rezervare efectuată cu succes!', 'rezervare_id': rezervare.id}), 201
    
    @staticmethod
    def verificare_disponibilitate(destinatie_id, data_inceput, data_sfarsit):
        destinatie = Destinatie.query.get(destinatie_id)
        if not destinatie:
            return False, 'Destinație inexistentă!'
        
        numar_zile = (data_sfarsit - data_inceput).days + 1
        numar_locuri_pe_zi = destinatie.numar_locuri

        for zi in range(numar_zile):
            data_curenta = data_inceput + timedelta(days=zi)
            rezervari_existente_pe_zi = Rezervare.query.filter(
                Rezervare.destinatie_id == destinatie_id,
                Rezervare.data_inceput <= data_curenta,
                Rezervare.data_sfarsit >= data_curenta
            ).count()

            if rezervari_existente_pe_zi >= numar_locuri_pe_zi:
                return False, f'Nu sunt suficiente locuri disponibile in aceasta perioada!'

        return True, 'Destinație disponibilă pentru rezervare.'
    
    @staticmethod
    def get_rezervari_for_destinatie(destinatie_id):
        rezervari = Rezervare.query.filter_by(destinatie_id=destinatie_id).all()
        serialized_rezervari = []
        for rezervare in rezervari:
            serialized_rezervari.append({
                'id': rezervare.id,
                'destinatie_id': rezervare.destinatie_id,
                'user_id': rezervare.user_id,
                'data_inceput': rezervare.data_inceput.strftime('%Y-%m-%d'),
                'data_sfarsit': rezervare.data_sfarsit.strftime('%Y-%m-%d'),
                'cost_total': rezervare.cost_total
            })
        return jsonify(serialized_rezervari), 200
    
    @staticmethod
    def numar_rezervari_in_luna(destinatie_id, an, luna):
        rezervari = Rezervare.query.filter(
        Rezervare.destinatie_id == destinatie_id,
        extract('year', Rezervare.data_inceput) == an,
        extract('month', Rezervare.data_inceput) == luna
     ).count()

        return rezervari
    