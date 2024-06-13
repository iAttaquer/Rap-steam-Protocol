from django.urls import path
from .views import load_schools_from_csv,schools#, #protocol_pdf# pdf_view,
from .views import ProtocolView, SchoolSelectionView


urlpatterns = [
    path('save-to-database', load_schools_from_csv, name='save-to-database'),
    path('', SchoolSelectionView.as_view(), name='wybor_szkoly'),
    path('wybor_szkoly2/', SchoolSelectionView.as_view(), name='wybor_szkoly2'),
    path('schools/', schools, name='schools'),
    # path('pdf_view', pdf_view, name='pdf_view'),
    # path('/protocol/<str:school_name>/', protocol_pdf, name='protocol_pdf'),
    path('protocol/<str:school_name>/', ProtocolView.as_view(), name='protocol_pdf'),
]