from django.contrib import admin

from .models import *

# Register your models here.

admin.register(User)
admin.register(Listing)
admin.register(Bid)
admin.register(Comment)