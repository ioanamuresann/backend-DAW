class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:root@localhost/travel'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'secret_key'