from django.test import TestCase
from .models import Wyznanie

# Create your tests here.


class WyznanieTestCase(TestCase):
    Wyznanie.objects.create()