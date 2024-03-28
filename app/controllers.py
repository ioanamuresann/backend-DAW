from flask import Blueprint, request, jsonify
from app.models import Destinatie, User
from app.services import DestinatieService, RezervareService, UserService
from datetime import datetime

auth_bp = Blueprint('auth', __name__)
destinatie_bp = Blueprint('destinatie', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    nume = data.get('nume')
    prenume = data.get('prenume')
    email = data.get('email')
    parola = data.get('parola')
    rol = data.get('rol')

    if not all([nume, prenume, email, parola, rol]):
        return jsonify({'message': 'Toate câmpurile sunt obligatorii!'}), 400

    if UserService.get_user_by_email(email):
        return jsonify({'message': 'Acest email există deja!'}), 400

    user = UserService.create_user(nume, prenume, email, parola, rol)
    return jsonify({'message': 'Utilizator înregistrat cu succes!', 'user_id': user.id}), 201

@auth_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    serialized_users = []
    for user in users:
        serialized_users.append({
            'id': user.id,
            'nume': user.nume,
            'prenume': user.prenume,
            'email': user.email,
            'rol': user.rol
        })
    return jsonify(serialized_users), 200

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    parola = data.get('parola')
    user = UserService.get_user_by_email(email)
    if user and user.check_password(parola):
        user_data = {
            'id': user.id,
            'nume': user.nume,
            'prenume': user.prenume,
            'email': user.email,
            'rol': user.rol
        }
        return jsonify({'user': user_data, 'message': 'Autentificare reușită!'}), 200
    return jsonify({'message': 'Eroare la autentificare! Verifică datele introduse.'}), 401

@destinatie_bp.route('/destinatii', methods=['GET'])
def get_destinatii():
    return DestinatieService.get_destinatii()

@destinatie_bp.route('/destinatii', methods=['POST'])
def create_destinatie():
    return DestinatieService.create_destinatie(request.json)

@destinatie_bp.route('/destinatii/<destinatie_id>', methods=['PUT'])
def update_destinatie(destinatie_id):
    return DestinatieService.update_destinatie(destinatie_id, request.json)

@destinatie_bp.route('/destinatii/<destinatie_id>', methods=['DELETE'])
def delete_destinatie(destinatie_id):
    return DestinatieService.delete_destinatie(destinatie_id)

@destinatie_bp.route('/destinatii/<destinatie_id>/rezervari', methods=['POST'])
def create_rezervare_for_destinatie(destinatie_id):
    data = request.json
    data_inceput = datetime.strptime(data.get('data_inceput'), '%Y-%m-%d')
    data_sfarsit = datetime.strptime(data.get('data_sfarsit'), '%Y-%m-%d')

    return RezervareService.create_rezervare(destinatie_id, data.get('user_id'), data_inceput, data_sfarsit)

@destinatie_bp.route('/destinatii/<destinatie_id>/verificare-disponibilitate', methods=['POST'])
def verificare_disponibilitate(destinatie_id):
    data = request.json
    data_inceput = datetime.strptime(data.get('data_inceput'), '%Y-%m-%d')
    data_sfarsit = datetime.strptime(data.get('data_sfarsit'), '%Y-%m-%d')

    disponibil, mesaj = RezervareService.verificare_disponibilitate(destinatie_id, data_inceput, data_sfarsit)
    if not disponibil:
        return jsonify({'message': mesaj})

    return jsonify({'message': 'Destinația este disponibilă în intervalul specificat.'}), 200

@destinatie_bp.route('/destinatii/<destinatie_id>/rezervari', methods=['GET'])
def get_rezervari_for_destinatie(destinatie_id):
    return RezervareService.get_rezervari_for_destinatie(destinatie_id)

@destinatie_bp.route('/destinatii/<destinatie_id>/rezervari/luna', methods=['POST'])
def numar_rezervari_luna(destinatie_id):
    data = request.get_json()
    an = data.get('an')
    luna = data.get('luna')

    if an is None or luna is None:
        return jsonify({'message': 'Anul și luna trebuie specificate în corpul cererii!'}), 400

    destinatie = Destinatie.query.get(destinatie_id)
    if not destinatie:
        return jsonify({'message': 'Destinație inexistentă!'}), 404

    numar_rezervari = RezervareService.numar_rezervari_in_luna(destinatie_id, an, luna)

    return jsonify(numar_rezervari), 200



