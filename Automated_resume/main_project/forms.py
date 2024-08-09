# forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.forms import SetPasswordForm


def validate_phone(value):
    if not value.isdigit():
        raise ValidationError('Phone number must contain only digits.')
    if len(value) != 10:
        raise ValidationError('Phone number must be exactly 10 digits.')


class ResumeForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField(validators=[validate_email])
    phone = forms.CharField(
        max_length=10,
        validators=[validate_phone],
        error_messages={'required': 'Phone number is required.'}
    )
    dob = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    resume = forms.FileField()


class QuestionForm(forms.Form):
    question = forms.CharField(widget=forms.HiddenInput(), required=False)
    option = forms.ChoiceField(choices=[], widget=forms.RadioSelect(), required=True)

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question', None)
        options = kwargs.pop('options', [])
        super(QuestionForm, self).__init__(*args, **kwargs)
        if question:
            self.fields['question'].initial = question
        self.fields['option'].choices = [(i, option) for i, option in options]


class AdminLoginForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=100, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class ResetPasswordDone(forms.Form):
    pass


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="Enter new password",
        widget=forms.PasswordInput,
        strip=False,
        help_text="Enter your new password",
    )
    new_password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput,
        strip=False,
        help_text="Enter the same password as before, for verification",
    )