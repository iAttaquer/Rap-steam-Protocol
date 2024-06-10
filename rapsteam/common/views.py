# -*- coding: utf-8 -*-
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
import os
os.environ["PISA_SHOW_LOG"] = "True"

from common.models import Address
from common.models import School, Settings, SchoolEquipment

from datetime import date, datetime

def HiWorld(request):
    return HttpResponse('Hello wordl!')

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
        nazwa_miasta = request.POST.get('miasto', '')
        if nazwa_szkoly:
            try:
                szkola = School.objects.filter(school_name=nazwa_szkoly)
                szkola = szkola.filter(address__city=nazwa_miasta).first()
                print(szkola)
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
    def get(self, request, school_name, *args, **kwargs):
        school_city = request.GET.get("miasto", '')
        school = School.objects.filter(school_name=school_name)
        school = school.filter(address__city=school_city).first()
        receipt_date = request.GET.get("selected-date", '')
        receipt_date = datetime.strptime(receipt_date, "%Y-%m-%d").strftime("%d.%m.%Y")
        contract_number = request.GET.get("selected-contract-number", '')
        
        kompl_realizacji = request.GET.get('kompl_tak') or request.GET.get('kompl_nie')
        
        zastrzezenia_kompl = request.GET.get('zastrz_kompl')
        zgodnosc_jakosci = request.GET.get('zgod_tak') or request.GET.get('zgod_nie')
        zastrzezenia_zgod = request.GET.get('zastrz_zgod')
        termin_wykonania = request.GET.get('term_tak') or request.GET.get('term_nie')
        zastrzezenia_term = request.GET.get('zastrz_term')
        kolejny_termin = request.GET.get('kole_tak') or request.GET.get('kole_nie')
        zastrzezenia_kole = request.GET.get('zastrz_kole')
        wynik_odbioru = request.GET.get('wyn_tak') or request.GET.get('wyn_nie')
        zastrzezenia_wyn = request.GET.get('zastrz_wyn')
        
        school_equipment = SchoolEquipment.objects.filter(school=school)
        equipment_with_data = []
        for i, equip in enumerate(school_equipment, start=1):
            equip.serial_numbers_list = equip.serial_numbers.split(',')
            delivery_status = request.GET.get(f'selected-delivery-status-{i}', '')
            comment = request.GET.get(f'typed-comment-{i}', '')
            equipment_with_data.append({
                'equip': equip,
                'delivery_status': delivery_status,
                'comment': comment,
            })
        print(equipment_with_data)
        settings = Settings.objects.last()
        logo_path = settings.pdf_protocol_logo.path if settings.pdf_protocol_logo else None
        
        context_dict = {
            "school_name": school.school_name,
            "city": school.address.city,
            "street": f' {school.address.street}',
            "house_number": school.address.house_number,
            "today_date": date.today().strftime("%d.%m.%Y"),
            "pdf_title": "Protokół {}".format(school.school_name),
            "director": f"{school.director.first_name} {school.director.last_name}",
            "logo": logo_path,
            "font": settings.pdf_protocol_font.url if settings.pdf_protocol_font else None,
            'receipt_date': receipt_date,
            'contract_number': contract_number,
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
            'school_equipment': equipment_with_data,  # Przekazujemy listę sprzętu z danymi
        }
        # print(context_dict)
        context = {'key': 'value'}
        return render_to_pdf("protocol_pdf.html", context_dict)

    def post(self, request, school_name, *args, **kwargs):
        # TODO: generate PDFs based on school data
        pass
        # school = School.objects.get(director=request.user, pk=pk)
        # school = get_object_or_404(School, school_name=school_name)
        # print(school)
        # receipt_date = request.POST.get("receipt_date")
        # # print(receipt_date)
        # nr_umowy = request.POST.get('nr_umowy')
        # kompl_realizacji = request.POST.get('kompl_tak') or request.POST.get('kompl_nie')
        # # print(kompl_realizacji)
        # zastrzezenia_kompl = request.POST.get('zastrz_kompl')
        # zgodnosc_jakosci = request.POST.get('zgod_tak') or request.POST.get('zgod_nie')
        # zastrzezenia_zgod = request.POST.get('zastrz_zgod')
        # termin_wykonania = request.POST.get('term_tak') or request.POST.get('term_nie')
        # zastrzezenia_term = request.POST.get('zastrz_term')
        # kolejny_termin = request.POST.get('kole_tak') or request.POST.get('kole_nie')
        # zastrzezenia_kole = request.POST.get('zastrz_kole')
        # wynik_odbioru = request.POST.get('wyn_tak') or request.POST.get('wyn_nie')
        # zastrzezenia_wyn = request.POST.get('zastrz_wyn')
        
        # sprzet_szkolny = SchoolEquipment.objects.filter(school=school)
        # sprzet_z_danymi = []
        # for i, sprzet in enumerate(sprzet_szkolny, start=1):
        #     sprzet.serial_numbers_list = sprzet.serial_numbers.split(',')
        #     status_dostarczenia = request.POST.get(f'status_dostarczenia_{i}', '')
        #     uwagi = request.POST.get(f'uwagi_{i}', '')
        #     sprzet_z_danymi.append({
        #         'sprzet': sprzet,
        #         'status_dostarczenia': status_dostarczenia,
        #         'uwagi': uwagi
        #     })
        # settings = Settings.objects.last()
        # logo_path = settings.pdf_protocol_logo.path if settings.pdf_protocol_logo else None
        
        # context_dict = {
        #     "school_name": school.school_name,
        #     "school_address": f"{school.address.city}, {school.address.street} {school.address.house_number}",
        #     "pdf_title": "Protokół {}".format(school.school_name),
        #     "director": f"{school.director.first_name} {school.director.last_name}",
        #     "logo": logo_path,
        #     "font": settings.pdf_protocol_font.url if settings.pdf_protocol_font else None,
        #     'receipt_date': receipt_date,
        #     'nr_umowy': nr_umowy,
        #     'kompl_realizacji': kompl_realizacji,
        #     'zastrzezenia_kompl': zastrzezenia_kompl,
        #     'zgodnosc_jakosci': zgodnosc_jakosci,
        #     'zastrzezenia_zgod': zastrzezenia_zgod,
        #     'termin_wykonania': termin_wykonania,
        #     'zastrzezenia_term': zastrzezenia_term,
        #     'kolejny_termin': kolejny_termin,
        #     'zastrzezenia_kole': zastrzezenia_kole,
        #     'wynik_odbioru': wynik_odbioru,
        #     'zastrzezenia_wyn': zastrzezenia_wyn,
        #     'sprzet_szkolny': sprzet_z_danymi,  # Przekazujemy listę sprzętu z danymi
        # }
        # print(context_dict)
        # # return render_to_pdf("protocol_pdf.html", context_dict)
        # # print(Settings.objects.all().last().pdf_protocol_logo)
        # if not school.goods_received:
        #     school.goods_received = True
        #     school.save()
        # else:
        #     return render_to_pdf("pdf_view.html", context_dict)
        #     response = render_to_pdf("protocol_pdf.html", context_dict)
        #     if response is None:
        #         return HttpResponse("Bład podczas generowania PDF", status=500)
        #     filename = f"{school.RSPO}.pdf"
        #     content = f"inline; filename={filename}"
        #     download = request.GET.get("download")
        #     if download:
        #         content = f"attachment; filename={filename}"
        #     response["Content-Disposition"] = content
        #     return response

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
    template = get_template(template_src)
    html = template.render(context_dict)
    # print("HTML content:", html)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result, encoding='UTF-8')
    if pdf.err:
        return HttpResponse("Invalid PDF", status_code=400, content_type='text/plain')
    return HttpResponse(result.getvalue(), content_type='application/pdf')

def pdf_view(request):
    context = {'key': 'value'}
    return render_to_pdf('pdf_view.html', context)