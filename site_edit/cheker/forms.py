from django import forms

class CheckSite(forms.Form):
    url = forms.URLField()