from django.apps import AppConfig
from django.conf import settings
import joblib


class AnprAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'anpr_app'
    current_dir = settings.BASE_DIR
    model_dir = current_dir / 'model/SVC_Model/SVC_Model.pkl'
    model = joblib.load(model_dir)
