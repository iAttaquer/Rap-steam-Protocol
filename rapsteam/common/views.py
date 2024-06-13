# -*- coding: utf-8 -*-
#from django.shortcuts import render

# Create your views here.
import csv
# from io import BytesIO

from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseServerError, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template, render_to_string
from django.views import View
from django.contrib.staticfiles import finders
# from xhtml2pdf import pisa
# import xhtml2pdf.pisa as pisa
import os
from django.contrib.staticfiles.storage import staticfiles_storage

from common.models import Address
from common.models import School, Settings, SchoolEquipment
from datetime import date, datetime

from django.conf import settings
import pdfkit
import subprocess


#path to wkhtmltopdf
config = pdfkit.configuration(wkhtmltopdf=r"C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe")

class SchoolSelectionView(View):
    def get(self, request, *args, **kwargs):
        if 'search' in request.GET:
            search_term = request.GET.get('search')
            school_exists = School.objects.filter(school_name__icontains=search_term).exists()
            return JsonResponse({'exists': school_exists})

        schools_list = School.objects.all()
        return render(request, 'index.html', {'schools_list': schools_list})

    def post(self, request, *args, **kwargs):
        school_name = request.POST.get('school-name', '')
        city = request.POST.get('city', '')
        if school_name:
            try:
                school = School.objects.filter(school_name=school_name)
                school = school.filter(address__city=city).first()
                request.session['school_name'] = school_name
                request.session['city'] = city

                school_address = school.address
                city = school_address.city
                street = school_address.street
                number = school_address.house_number

                school_equipment = []
                for equip in SchoolEquipment.objects.filter(school=school):
                    equip.serial_numbers_list = equip.serial_numbers.split(',')
                    school_equipment.append(equip)

                return render(request, 'wybor_szkoly2.html', {
                    'school_name': school_name,
                    'city': city,
                    'street': street,
                    'number': number,
                    'school_equipment': school_equipment,
                })
            except School.DoesNotExist:
                return redirect('wybor_szkoly')
        else:
            return redirect('wybor_szkoly')


class ProtocolView(View):
    def get(self, request, *args, **kwargs):
        context_dict = request.session.get('context_dict',{})
        if 'school_equipment' in context_dict:
            context_dict['school_equipment'] = [
                {
                    'name': equip['name'],
                    'quantity': equip['quantity'],
                    'serial_numbers_list': equip['serial_numbers_list'],
                    'delivery_status': equip.get('delivery_status'),
                    'comment': equip.get('comment'),
                }
                for equip in context_dict['school_equipment']
            ]
        return render_to_pdf('protocol_pdf.html', context_dict)

    def post(self, request, school_name, *args, **kwargs):
        school_name = request.session.get('school_name')
        school_city = request.session.get('city', '')
        school = School.objects.filter(school_name=school_name)
        school = school.filter(address__city=school_city).first()

        if not school:
            return HttpResponseServerError("Nie znaleziono szkoły")

        receipt_date = request.POST.get("receipt-date", '')
        receipt_date = datetime.strptime(receipt_date, "%Y-%m-%d").strftime("%d.%m.%Y")
        contract_number = request.POST.get("contract-number", '')
        completeness_yes = request.POST.get("completeness-yes")
        completeness_no = request.POST.get("completeness-no")
        caveats_completeness = request.POST.get("caveats-completeness", '')
        compliance_yes = request.POST.get("compliance-yes")
        compliance_no = request.POST.get("compliance-no")
        caveats_compliance = request.POST.get("caveats-compliance", '')
        term_yes = request.POST.get("term-yes")
        term_no = request.POST.get("term-no")
        caveats_term = request.POST.get("caveats-term", '')
        result_yes = request.POST.get("result-yes")
        result_no = request.POST.get("result-no")
        caveats_result = request.POST.get("caveats-result", '')

        school_equipment = SchoolEquipment.objects.filter(school=school)
        equipment_with_data = []
        for i, equip in enumerate(school_equipment, start=1):
            equip.serial_numbers_list = equip.serial_numbers.split(',')
            delivery_status = request.POST.get(f'delivery-status-{i}', '')
            comment = request.POST.get(f'comment-{i}', '')
            equipment_with_data.append({
                'equip': equip,
                'delivery_status': delivery_status,
                'comment': comment,
            })
        settings = Settings.objects.last()
        logo_path = settings.pdf_protocol_logo.path if settings.pdf_protocol_logo else None
        font_path = settings.pdf_protocol_font.path if settings.pdf_protocol_font else None

        context_dict = {
            "filename": school.RSPO,
            "school_name": school.school_name,
            "city": school.address.city,
            "street": f' {school.address.street}',
            "house_number": school.address.house_number,
            "today_date": date.today().strftime("%d.%m.%Y"),
            "pdf_title": "Protokół {}".format(school.school_name),
            "director": f"{school.director.first_name} {school.director.last_name}",
            "logo": logo_path,
            "font": font_path,
            "receipt_date": receipt_date,
            "contract_number": contract_number,
            "completeness_yes": completeness_yes,
            "completeness_no": completeness_no,
            "caveats_completeness": caveats_completeness,
            "compliance_yes": compliance_yes,
            "compliance_no": compliance_no,
            "caveats_compliance": caveats_compliance,
            "term_yes": term_yes,
            "term_no": term_no,
            "caveats_term": caveats_term,
            "result_yes": result_yes,
            "result_no": result_no,
            "caveats_result": caveats_result,
            "school_equipment": [
                {
                    'name': equip.equipment.name,
                    'quantity': equip.quantity,
                    'serial_numbers_list': equip.serial_numbers.split(','),
                    'delivery_status': request.POST.get(f'delivery-status-{i+1}', ''),
                    'comment': request.POST.get(f'comment-{i+1}', ''),
                }
                for i, equip in enumerate(school_equipment)
            ]
        }
        request.session['context_dict'] = context_dict
        return render_to_pdf('protocol_pdf.html', context_dict)



    # def post(self, request, school_name, *args, **kwargs):
    #     # TODO: generate PDFs based on school data
        # school = School.objects.get(director=request.user, pk=pk)
        # school = get_object_or_404(School, school_name=school_name)
        # print(school)
        # receipt_date = request.POST.get("receipt_date")
        # # print(receipt_date)
        # nr_umowy = request.POST.get('nr_umowy')
        
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
    options = {
        '--enable-local-file-access': '',
        '--load-error-handling': 'ignore',
        '--quiet': '',
        '--margin-top': '15mm',
        '--margin-bottom': '15mm',
        '--margin-left': '12mm',
        '--margin-right': '12mm',
        'encoding': "UTF-8",
    }
    try:
        pdf = pdfkit.from_string(html, False, configuration=config, options=options)
    except subprocess.CalledProcessError as e:
        return HttpResponse(f"Error generating PDF: {e.output.decode()}", status_code=500, content_type='text/plain')

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{context_dict['filename']}.pdf"'
    return response

# Function to render pdf using xhtml2pdf (not rendering polish characters)
# def render_to_pdf(template_src, context_dict):
#     template = get_template(template_src)
#     html = template.render(context_dict)
#     # print("HTML content:", html)
#     result = BytesIO()
#     pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, encoding='UTF-8', path=context_dict['font'])
#     # pdf = pisa.pisaDocument(html, result, encoding='UTF-8', path=context_dict['font'])
#     if pdf.err:
#         return HttpResponse("Invalid PDF", status_code=400, content_type='text/plain')
#     return HttpResponse(result.getvalue(), content_type='application/pdf')
