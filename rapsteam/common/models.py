#from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.db import models

#from common.models import Address
class Address(models.Model):
    city = models.CharField(max_length=255, verbose_name="Miejscowość")
    street = models.CharField(max_length=255, verbose_name="Ulica")
    district = models.CharField(max_length=255, verbose_name="Powiat")
    commune = models.CharField(max_length=255, verbose_name="Gmina")
    house_number = models.CharField(max_length=255, verbose_name="Numer domu")
    
    class Meta:
        verbose_name = 'Adres'
        verbose_name_plural = 'Adresy'

class School(models.Model):
    RSPO = models.IntegerField(verbose_name="RSPO", unique=True)
    nip = models.BigIntegerField(verbose_name="NIP")
    school_name = models.CharField(max_length=255, verbose_name="Nazwa szkoły")
    phone = models.CharField(max_length=15, verbose_name="Telefon kontaktowy szkoły")
    email = models.EmailField(verbose_name="Szkolny kontaktowy adres e-mail")

    director_first_name = models.CharField(max_length=255, verbose_name="Dyrektor imię")
    director_last_name = models.CharField(max_length=255, verbose_name="Dyrektor nazwisko")
    total_students = models.IntegerField(verbose_name="Uczniów")

    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='address_schools', verbose_name="Adres")
    director = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='directed_schools',
                                 verbose_name="Dyrektor", null=True, blank=True)

    goods_received = models.BooleanField(default=False, null=True, blank=True, verbose_name='Otrzymane towary')
    acceptance_protocol = models.FileField(null=True, blank=True, verbose_name='Protokół odbioru')
    
    equipment = models.ManyToManyField('Equipment', through='SchoolEquipment', verbose_name="Sprzęt")

    def __str__(self):
        return f'{self.school_name} ({self.address.city})'

    class Meta:
        verbose_name = 'Szkoła'
        verbose_name_plural = 'Szkoły'


class Settings(models.Model):
    csv_string_RSPO = models.CharField(max_length=255, blank=True, null=True, default="RSPO", verbose_name="RSPO")
    csv_string_nip = models.CharField(max_length=255, blank=True, null=True, default="nip", verbose_name="NIP")
    csv_string_school_name = models.CharField(max_length=255, blank=True, null=True, default="Nazwa szkoły",
                                              verbose_name="Nazwa szkoły")
    csv_string_phone = models.CharField(max_length=255, blank=True, null=True, default="tel.",
                                        verbose_name="Telefon kontaktowy szkoły")
    csv_string_email = models.CharField(max_length=255, blank=True, null=True, default="email",
                                        verbose_name="Szkolny kontaktowy adres e-mail")
    csv_string_total_students = models.CharField(max_length=255, blank=True, null=True, default="suma",
                                                 verbose_name="Uczniów")
    csv_string_director_first_name = models.CharField(max_length=255, blank=True, null=True, default="Imię dyr.",
                                                      verbose_name="Dyrektor imię")
    csv_string_director_last_name = models.CharField(max_length=255, blank=True, null=True, default="Nazwisko dyr.",
                                                     verbose_name="Dyrektor nazwisko")
    csv_string_city = models.CharField(max_length=255, blank=True, null=True, default="Miejscowość",
                                       verbose_name="Miejscowość")
    csv_string_street = models.CharField(max_length=255, blank=True, null=True, default="Ulica", verbose_name="Ulica")
    csv_string_house_number = models.CharField(max_length=10, blank=True, null=True, default="Numer domu",
                                               verbose_name="Numer domu")
    csv_string_district = models.CharField(max_length=255, blank=True, null=True, default="Powiat",
                                           verbose_name="Powiat")
    csv_string_commune = models.CharField(max_length=255, blank=True, null=True, default="Gmina", verbose_name="Gmina")
    pdf_protocol_logo = models.ImageField(upload_to='public/uploads/', blank=True, null=True,
                                          verbose_name='Czcionka protokołu PDF')
    pdf_protocol_font = models.FileField(upload_to='public/uploads/', blank=True, null=True,
                                         verbose_name='Logo protokołu PDF')

    class Meta:
        verbose_name = "Ustawienie"
        verbose_name_plural = "Ustawienia"

    def __str__(self):
        return f'Ustawienie {self.pk}'

        
class Equipment(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nazwa sprzętu")
    description = models.TextField(verbose_name="Opis sprzętu", blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} ({self.description})"
    
    class Meta:
        verbose_name = "Sprzęt"
        verbose_name_plural = "Sprzęty"
        

class SchoolEquipment(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='school_equipment', verbose_name="Szkoła")
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='school_equipment', verbose_name="Sprzęt")
    quantity = models.PositiveIntegerField(verbose_name="Ilość")
    serial_numbers = models.CharField(max_length=255, verbose_name="Numery seryjne", blank=True, null=True)
    
    def __str__(self):
        return f"{self.school.school_name} - {self.equipment.name} ({self.quantity})"
    
    class Meta:
        verbose_name = "Sprzęt szkolny"
        verbose_name_plural = "Sprzęt szkolny"
        
    