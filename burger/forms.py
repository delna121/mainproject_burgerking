from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import *
from .models import OrderPlaced

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        help_texts = {
            'username': None,
            'email': None,
            'password1': None,
            'password2': None,
        }
        

class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name','phone','address','city','state','zipcode']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone':forms.NumberInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.Select(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'zipcode': forms.NumberInput(attrs={'class': 'form-control'}),
        }
class OrderForm(forms.ModelForm):
    class Meta:
        model = OrderPlaced
        fields = ['user','status']

class CouponApplyForm(forms.Form):
    code = forms.CharField()

class ProductForm(forms.ModelForm):
    excel_file = forms.FileField(required=True)

    class Meta:
        model = Product
        fields = '__all__'