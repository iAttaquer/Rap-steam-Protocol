from django.urls import path
from .views import HiWorld,load_schools_from_csv,schools, pdf_view#, GeneratePDFView #, wybor_szkoly,  wybor_szkoly2,
from .views import ProtocolView, SchoolSelectionView


urlpatterns = [
    path('test', HiWorld, name='test'),
    path('save-to-database', load_schools_from_csv, name='save-to-database'),
    # path('', wybor_szkoly, name='wybor_szkoly'),
    path('', SchoolSelectionView.as_view(), name='wybor_szkoly'),
    # path('wybor_szkoly2/', wybor_szkoly2, name='wybor_szkoly2'),
    path('wybor_szkoly2/', SchoolSelectionView.as_view(), name='wybor_szkoly2'),
    path('schools/', schools, name='schools'),
    path('pdf_view', pdf_view, name='pdf_view'),
    path('protocol/<str:school_name>/', ProtocolView.as_view(), name='protocol_pdf'),
    # path('generate_pdf/', GeneratePDFView.as_view(), name='generate_pdf'),
]