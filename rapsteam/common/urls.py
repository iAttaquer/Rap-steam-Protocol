from django.urls import path
from .views import HiWorld,load_schools_from_csv


urlpatterns = [
    path('test', HiWorld, name='test'),
    path('save-to-database', load_schools_from_csv, name='save-to-database')
]