# forms.py
from django import forms



class UserLookupForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)



# create a form field for a large text area - for example, a text that can take up to a a4 page
class LargeTextAreaForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)
