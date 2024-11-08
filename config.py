# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_very_secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///household_services.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False