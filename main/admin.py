from django.contrib import admin
from main.models import Wyznanie, Komentarz, Answer, Avatar

# Register your models here.

admin.site.register(Wyznanie)
admin.site.register(Komentarz)
admin.site.register(Answer)
admin.site.register(Avatar)