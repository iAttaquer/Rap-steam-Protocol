#from django.shortcuts import render

# Create your views here.
import csv
from io import BytesIO

from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseServerError, JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa
import xhtml2pdf.pisa as pisa

from common.models import Address
from common.models import School, Settings, SchoolEquipment

def HiWorld(request):
    return HttpResponse('Hello wordl!')

def wybor_szkoly(request):
    lista_szkol = School.objects.all()

    if request.method == 'GET' and 'search' in request.GET:
        search_term = request.GET.get('search')
        szkola_istnieje = School.objects.filter(school_name__icontains=search_term).exists()
        return JsonResponse({'exists': szkola_istnieje})
    return render(request, 'index.html', {'lista_szkol': lista_szkol})

def wybor_szkoly2(request):
    nazwa_szkoly = request.GET.get('szkola', '')
    if nazwa_szkoly:
        try:
            szkola = School.objects.get(school_name=nazwa_szkoly)
            request.session['nazwa_szkoly'] = nazwa_szkoly
            
            adres_szkoly = szkola.address
            miasto = adres_szkoly.city
            ulica = adres_szkoly.street
            numer = adres_szkoly.house_number
            
            return render(request, 'wybor_szkoly2.html', {
                'nazwa_szkoly': nazwa_szkoly,
                'miasto': miasto,
                'ulica': ulica,
                'numer': numer,
            })
        except School.DoesNotExist:
            return redirect('wybor_szkoly')
    else:
        return redirect('wybor_szkoly')

    # return render(request, 'wybor_szkoly2.html', {'nazwa_szkoly': nazwa_szkoly})

class ProtocolView(View):
    def get(self, request, *args, **kwargs):
        schools = School.objects.filter(director=request.user)
        return render(request,
                      context={"schools": schools},
                      template_name='schools/protocol.html')

    def post(self, request, pk, *args, **kwargs):
        # TODO: generate PDFs based on school data
        school = School.objects.get(director=request.user, pk=pk)
        context_dict = {
            "school_name": school.school_name,
            "pdf_title": "Protokół {}".format(school.school_name),
            "director": f"{school.director.first_name} {school.director.last_name}",
            "logo": Settings.objects.all().last().pdf_protocol_logo.path,
            "font": Settings.objects.all().last().pdf_protocol_font.path
        }
        # print(Settings.objects.all().last().pdf_protocol_logo)
        if not school.goods_received:
            school.goods_received = True
            school.save()
        else:
            response = render_to_pdf("schools/protocol_pdf.html", context_dict)
            filename = f"{school.RSPO}.pdf"
            content = f"inline; filename={filename}"
            download = request.GET.get("download")
            if download:
                content = f"attachment; filename={filename}"
            response["Content-Disposition"] = content
            return response

        schools = School.objects.filter(director=request.user)
        return render(request,
                      context={"schools": schools},
                      template_name='schools/protocol.html')


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
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
    if pdf.err:
        return HttpResponse("Invalid PDF", status_code=400, content_type='text/plain')
    return HttpResponse(result.getvalue(), content_type='application/pdf')

def pdf_view(request):
    context = {'key': 'value'}
    return render_to_pdf('pdf_view.html', context)