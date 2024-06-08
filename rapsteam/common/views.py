#from django.shortcuts import render

# Create your views here.
import csv
from io import BytesIO

from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseServerError, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa
import xhtml2pdf.pisa as pisa


from common.models import Address
from common.models import School, Settings, SchoolEquipment

def HiWorld(request):
    return HttpResponse('Hello wordl!')

# def wybor_szkoly(request):
#     lista_szkol = School.objects.all()

#     if request.method == 'GET' and 'search' in request.GET:
#         search_term = request.GET.get('search')
#         szkola_istnieje = School.objects.filter(school_name__icontains=search_term).exists()
#         return JsonResponse({'exists': szkola_istnieje})
#     return render(request, 'index.html', {'lista_szkol': lista_szkol})

# def wybor_szkoly2(request):
#     nazwa_szkoly = request.GET.get('szkola', '')
#     if nazwa_szkoly:
#         try:
#             szkola = School.objects.get(school_name=nazwa_szkoly)
#             request.session['nazwa_szkoly'] = nazwa_szkoly
            
#             adres_szkoly = szkola.address
#             miasto = adres_szkoly.city
#             ulica = adres_szkoly.street
#             numer = adres_szkoly.house_number
            
#             sprzet_szkolny = []
#             for sprzet in SchoolEquipment.objects.filter(school=szkola):
#                 sprzet.serial_numbers_list = sprzet.serial_numbers.split(',')
#                 sprzet_szkolny.append(sprzet)
            
#             return render(request, 'wybor_szkoly2.html', {
#                 'nazwa_szkoly': nazwa_szkoly,
#                 'miasto': miasto,
#                 'ulica': ulica,
#                 'numer': numer,
#                 'sprzet_szkolny': sprzet_szkolny,
#             })
#         except School.DoesNotExist:
#             return redirect('wybor_szkoly')
#     else:
#         return redirect('wybor_szkoly')

    # return render(request, 'wybor_szkoly2.html', {'nazwa_szkoly': nazwa_szkoly})

class SchoolSelectionView(View):
    def get(self, request, *args, **kwargs):
        if 'search' in request.GET:
            search_term = request.GET.get('search')
            szkola_istnieje = School.objects.filter(school_name__icontains=search_term).exists()
            return JsonResponse({'exists': szkola_istnieje})
        
        lista_szkol = School.objects.all()
        return render(request, 'index.html', {'lista_szkol': lista_szkol})

    def post(self, request, *args, **kwargs):
        nazwa_szkoly = request.POST.get('szkola', '')
        if nazwa_szkoly:
            try:
                szkola = School.objects.get(school_name=nazwa_szkoly)
                request.session['nazwa_szkoly'] = nazwa_szkoly
                
                adres_szkoly = szkola.address
                miasto = adres_szkoly.city
                ulica = adres_szkoly.street
                numer = adres_szkoly.house_number
                
                sprzet_szkolny = []
                for sprzet in SchoolEquipment.objects.filter(school=szkola):
                    sprzet.serial_numbers_list = sprzet.serial_numbers.split(',')
                    sprzet_szkolny.append(sprzet)
                    
                return render(request, 'wybor_szkoly2.html', {
                    'nazwa_szkoly': nazwa_szkoly,
                    'miasto': miasto,
                    'ulica': ulica,
                    'numer': numer,
                    'sprzet_szkolny': sprzet_szkolny,
                })
            except School.DoesNotExist:
                return redirect('wybor_szkoly')
        else:
            return redirect('wybor_szkoly')
class ProtocolView(View):
    def get(self, request, *args, **kwargs):
        # schools = School.objects.filter(director=request.user)
        # return render(request,
        #               context={"schools": schools},
        #               template_name='schools/protocol.html')
        nazwa_szkoly = request.session.get('nazwa_szkoly')
        sprzet_szkolny = []
        
        if nazwa_szkoly:
            try:
                szkola = School.objects.get(school_name=nazwa_szkoly)
                for sprzet in SchoolEquipment.objects.filter(school=szkola):
                    sprzet.serial_numbers_list = sprzet.serial_numbers.split(',')
                    sprzet_szkolny.append(sprzet)

                return render(request, 'wybor_szkoly2.html', {
                    'nazwa_szkoly': nazwa_szkoly,
                    'miasto': szkola.address.city,
                    'ulica': szkola.address.street,
                    'numer': szkola.address.house_number,
                    'sprzet_szkolny': sprzet_szkolny,
                })
            except School.DoesNotExist:
                return redirect('wybor_szkoly')
        else:
            return redirect('wybor_szkoly')

    def post(self, request, school_name, *args, **kwargs):
        # TODO: generate PDFs based on school data
        # school = School.objects.get(director=request.user, pk=pk)
        school = get_object_or_404(School, school_name=school_name)
        
        data_odbioru = request.POST.get('data_odbioru')
        nr_umowy = request.POST.get('nr_umowy')
        kompl_realizacji = request.POST.get('kompl_tak') or request.POST.get('kompl_nie')
        zastrzezenia_kompl = request.POST.get('zastrz_kompl')
        zgodnosc_jakosci = request.POST.get('zgod_tak') or request.POST.get('zgod_nie')
        zastrzezenia_zgod = request.POST.get('zastrz_zgod')
        termin_wykonania = request.POST.get('term_tak') or request.POST.get('term_nie')
        zastrzezenia_term = request.POST.get('zastrz_term')
        kolejny_termin = request.POST.get('kole_tak') or request.POST.get('kole_nie')
        zastrzezenia_kole = request.POST.get('zastrz_kole')
        wynik_odbioru = request.POST.get('wyn_tak') or request.POST.get('wyn_nie')
        zastrzezenia_wyn = request.POST.get('zastrz_wyn')
        
        sprzet_szkolny = SchoolEquipment.objects.filter(school=school)
        sprzet_z_danymi = []
        for i, sprzet in enumerate(sprzet_szkolny, start=1):
            sprzet.serial_numbers_list = sprzet.serial_numbers.split(',')
            status_dostarczenia = request.POST.get(f'status_dostarczenia_{i}', '')
            uwagi = request.POST.get(f'uwagi_{i}', '')
            sprzet_z_danymi.append({
                'sprzet': sprzet,
                'status_dostarczenia': status_dostarczenia,
                'uwagi': uwagi
            })
        settings = Settings.objects.last()
        logo_path = settings.pdf_protocol_logo.path if settings.pdf_protocol_logo else None
        
        context_dict = {
            "school_name": school.school_name,
            "school_address": f"{school.address.city}, {school.address.street} {school.address.house_number}",
            "pdf_title": "Protokół {}".format(school.school_name),
            "director": f"{school.director.first_name} {school.director.last_name}",
            "logo": logo_path,
            "font": settings.pdf_protocol_font.url if settings.pdf_protocol_font else None,
            'data_odbioru': data_odbioru,
            'nr_umowy': nr_umowy,
            'kompl_realizacji': kompl_realizacji,
            'zastrzezenia_kompl': zastrzezenia_kompl,
            'zgodnosc_jakosci': zgodnosc_jakosci,
            'zastrzezenia_zgod': zastrzezenia_zgod,
            'termin_wykonania': termin_wykonania,
            'zastrzezenia_term': zastrzezenia_term,
            'kolejny_termin': kolejny_termin,
            'zastrzezenia_kole': zastrzezenia_kole,
            'wynik_odbioru': wynik_odbioru,
            'zastrzezenia_wyn': zastrzezenia_wyn,
            'sprzet_szkolny': sprzet_z_danymi,  # Przekazujemy listę sprzętu z danymi
        }
        
        
        # print(Settings.objects.all().last().pdf_protocol_logo)
        if not school.goods_received:
            school.goods_received = True
            school.save()
        else:
            return render_to_pdf("protocol_pdf.html", context_dict)
            response = render_to_pdf("protocol_pdf.html", context_dict)
            if response is None:
                return HttpResponse("Bład podczas generowania PDF", status=500)
            filename = f"{school.RSPO}.pdf"
            content = f"inline; filename={filename}"
            download = request.GET.get("download")
            if download:
                content = f"attachment; filename={filename}"
            response["Content-Disposition"] = content
            return response

        # schools = School.objects.filter(director=request.user)
        # return render(request,
        #               context={"schools": schools},
        #               template_name='templates/protocol.html')


def load_schools_from_csv(request):
    with open("schools.csv", 'r', encoding='utf-8') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        settings = Settings.objects.last()
        if not settings:
            raise ValueError("Settings object not found, create it first")

        for idx, row in enumerate(csv_reader):
            try:
                school_data = {
                    'RSPO': int(row[settings.csv_string_RSPO]),
                    'nip': int(row[settings.csv_string_nip]),
                    'school_name': row[settings.csv_string_school_name],
                    'phone': row[settings.csv_string_phone],
                    'email': row[settings.csv_string_email].lower(),
                    'total_students': int(row[settings.csv_string_total_students]),
                    'director_first_name': row[settings.csv_string_director_first_name],
                    'director_last_name': row[settings.csv_string_director_last_name],
                }
                address_data = {
                    'city': row[settings.csv_string_city],
                    'street': row[settings.csv_string_street],
                    'district': row[settings.csv_string_district],
                    'commune': row[settings.csv_string_commune],
                    'house_number': row[settings.csv_string_house_number],
                }
                director_data = {
                    'first_name': row[settings.csv_string_director_first_name],
                    'last_name': row[settings.csv_string_director_last_name],
                    'email': row[settings.csv_string_email].lower(),
                    'username': row[settings.csv_string_email].lower(),
                }

                director = None
                if row[settings.csv_string_email]:
                    director, created = User.objects.update_or_create(
                        email=director_data['email'],
                        defaults=director_data
                    )

                address, created = Address.objects.update_or_create(
                    city=address_data['city'],
                    district=address_data['district'],
                    commune=address_data['commune'],
                    house_number=address_data['house_number'],
                    defaults=address_data
                )

                school_data["address"] = address
                school_data["director"] = director
                school, created = School.objects.update_or_create(
                    RSPO=school_data['RSPO'],
                    defaults=school_data
                )

                if not created:
                    print("DUPLICATE", school_data['RSPO'], school_data['school_name'], school_data['phone'])
            except Exception as e:
                print(e)
                print(row)
    return HttpResponse('hejka')

def schools(request):
    return render(request, 'schools.html')

def render_to_pdf(template_src, context_dict):
    print("Rendering PDF...")
    template = get_template(template_src)
    html = template.render(context_dict)
    print("HTML content:", html)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
    if pdf.err:
        print("Error generating PDF:", pdf.err)
        return None
        return HttpResponse("Invalid PDF", status_code=400, content_type='text/plain')
    return HttpResponse(result.getvalue(), content_type='application/pdf')

def pdf_view(request):
    context = {'key': 'value'}
    return render_to_pdf('pdf_view.html', context)