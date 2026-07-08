from django.contrib import admin

from .models import User,Applicant

admin.site.register([User,Applicant])
