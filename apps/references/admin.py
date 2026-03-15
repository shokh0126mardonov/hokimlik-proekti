from django.contrib import admin

from .models import ApplicationType,Mahalla,Service

admin.site.register([ApplicationType,Mahalla,Service])