from app import db
import uuid
from datetime import datetime
from sqlalchemy.orm import relationship

class User(db.Model):
    id = db.Column(db.String, primary_key=True)
    nume = db.Column(db.String(50))
    prenume = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True)
    parola = db.Column(db.String(100))
    rol = db.Column(db.String(10))
    rezervari = relationship("Rezervare", back_populates="user")

    def check_password(self, parola):
        return self.parola == parola
    
class Destinatie(db.Model):
    id = db.Column(db.String, primary_key=True)
    titlu = db.Column(db.String(100), nullable=False)
    descriere = db.Column(db.Text, nullable=False)
    locatie = db.Column(db.String(100), nullable=False)
    pret_per_noapte = db.Column(db.Float, nullable=False)
    numar_locuri = db.Column(db.Integer, nullable=False)
    procent_reducere = db.Column(db.Integer, default=0)
    imagine = db.Column(db.String(255))
    rezervari = relationship("Rezervare", back_populates="destinatie")

    def __init__(self, titlu, descriere, locatie, pret_per_noapte, numar_locuri, imagine, procent_reducere=0):
        self.id = str(uuid.uuid4())
        self.titlu = titlu
        self.descriere = descriere
        self.locatie = locatie
        self.pret_per_noapte = pret_per_noapte
        self.numar_locuri = numar_locuri
        self.procent_reducere = procent_reducere
        self.imagine = imagine

class Rezervare(db.Model):
    id = db.Column(db.String, primary_key=True)
    destinatie_id = db.Column(db.String, db.ForeignKey('destinatie.id'), nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('user.id'), nullable=False)
    data_rezervare = db.Column(db.DateTime, nullable=False, default=datetime.now)
    data_inceput = db.Column(db.DateTime, nullable=False)
    data_sfarsit = db.Column(db.DateTime, nullable=False)
    cost_total = db.Column(db.Float, nullable=False)

    destinatie = relationship("Destinatie", back_populates="rezervari")
    user = relationship("User", back_populates="rezervari")

    def __init__(self, destinatie_id, user_id, data_inceput, data_sfarsit, cost_total):
        self.id = str(uuid.uuid4())
        self.destinatie_id = destinatie_id
        self.user_id = user_id
        self.data_inceput = data_inceput
        self.data_sfarsit = data_sfarsit
        self.cost_total = cost_total