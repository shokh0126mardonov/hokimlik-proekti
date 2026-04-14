from django.contrib import admin

from .models import Attachment,Application,MahallaReport

admin.site.register([Attachment,Application,MahallaReport])