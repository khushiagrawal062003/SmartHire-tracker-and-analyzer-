from django import forms
from django.core.exceptions import ValidationError

class JobApplicationForm(forms.Form):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('interviewing', 'Interviewing'),
        ('offered', 'Offered'),
        ('rejected', 'Rejected')
    ]
    
    company_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Google'})
    )
    job_title = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Python Developer'})
    )
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    salary = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 85,000'})
    )
    deadline = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    contact_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'hr@company.com'})
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Paste job descriptions, requirements or roles here...'})
    )

    def clean_company_name(self):
        data = self.cleaned_data['company_name']
        if not data.strip():
            raise ValidationError("Company name cannot be blank.")
        return data.strip()

    def clean_job_title(self):
        data = self.cleaned_data['job_title']
        if not data.strip():
            raise ValidationError("Job title cannot be blank.")
        return data.strip()
