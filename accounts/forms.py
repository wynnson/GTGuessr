from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe
from .models import User

class CustomErrorList(ErrorList):
    def __str__(self):
        if not self:
            return ''
        return mark_safe(''.join([
            f'<div class="bg-red-100 text-red-700 p-2 rounded mb-2">{e}</div>'
            for e in self
        ]))

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "username": "Choose a GTGuessr name",
            "email": "George.P.Burdell@gatech.edu",
            "password1": "Create a password",
            "password2": "Re-enter your password",
        }

        for fieldname, field in self.fields.items():
            field.help_text = None
            field.widget.attrs.update({
                "class": (
                    "block w-full px-3 py-2 border border-gray-300 rounded-md "
                    "focus:outline-none focus:ring-2 focus:ring-gtgold focus:border-gtgold text-gtblue"
                ),
                "placeholder": placeholders.get(fieldname, f"Enter {field.label.lower()}"),
            })