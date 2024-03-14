# forms.py
from django import forms

class UserLookupForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)