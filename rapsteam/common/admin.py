from django.contrib import admin
from .models import Address,School,Settings

# Register your models here.

admin.site.register(Address)
admin.site.register(School)
admin.site.register(Settings)