from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class PpastUserCreationForm(UserCreationForm):
    username = forms.CharField(strip=False)
    email = forms.CharField(strip=False)
    first_name = forms.CharField(strip=False)
    last_name = forms.CharField(strip=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ("email", "first_name", "last_name",  "company_name", "address", "phone_number", "postal_code", "city", "country", "province", "is_enterprise_admin")
        abstract = True



class PpastMemberCreationForm(UserCreationForm):
    username = forms.CharField(strip=False)
    email = forms.CharField(strip=False)
    first_name = forms.CharField(strip=False)
    last_name = forms.CharField(strip=False)
    is_enterprise_member = forms.BooleanField()
    # created_by = forms.InlineForeignKeyField()

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ("email", "first_name", "last_name", "is_enterprise_member")
        abstract = True
