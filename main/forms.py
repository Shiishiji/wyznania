from django import forms
from django.utils.translation import ugettext_lazy as _

from main.models import Answer, Wyznanie, Komentarz


class FormaWyznanie(forms.ModelForm):

    error_css_class = 'error'
    required_css_class = 'required'

    class Meta:
        model = Wyznanie
        fields = ['title', 'tresc']
        labels = {
            'title': _('Tytuł'),
            'tresc': _('Treść'),
        }
        error_messages = {
            'title': {
                'max_length': _('Twój tytuł jest za długi! Wymyśl coś krótszego :('),
            },
            'tresc': {
                'max_length': _('Twoje wyznanie jest za długie!'),
            },
        }

    def clean(self):
        cleaned_data = super(FormaWyznanie, self).clean()
        title = cleaned_data.get('title')
        tresc = cleaned_data.get('tresc')
        if title and tresc:
            if len(title) > len(tresc):
                raise forms.ValidationError(_("Tytuł wyznania nie może być dłuższy niż jego treść!"), code='spam')


class FormaKomentarz(forms.ModelForm):

    class Meta:
        model = Komentarz
        fields = ['tresc']
        labels = {
            'tresc': _(''),  # no label
        }


class FormAnswer(forms.ModelForm):

    class Meta:
        model = Answer
        fields = ['tresc']
        labels = {
            'tresc': _(''),  # no label
        }