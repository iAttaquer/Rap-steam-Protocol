from django.urls import path
from .views import HiWorld,load_schools_from_csv, wybor_szkoly, schools, pdf_view


urlpatterns = [
    path('test', HiWorld, name='test'),
    path('save-to-database', load_schools_from_csv, name='save-to-database'),
    path('', wybor_szkoly, name='wybor_szkoly'),
    path('schools/', schools, name='schools'),
    path('pdf_view', pdf_view, name='pdf_view'),
]