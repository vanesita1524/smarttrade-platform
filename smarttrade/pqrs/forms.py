# pqrs/forms.py
from django import forms
from .models import PQRS

class PQRSForm(forms.ModelForm):
    class Meta:
        model = PQRS
        fields = ['nombre', 'correo', 'mensaje']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre completo'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Tu correo electrónico'}),
            'mensaje': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Escribe tu solicitud, queja o felicitación...'}),
        }