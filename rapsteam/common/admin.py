from django.contrib import admin
from .models import Address,School,Settings,EquipmentType, Equipment, SchoolEquipment
# Register your models here.

admin.site.register(Address)
admin.site.register(School)
admin.site.register(Settings)
admin.site.register(EquipmentType)
admin.site.register(Equipment)
admin.site.register(SchoolEquipment)