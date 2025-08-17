
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################


# AQUÍ ES DONDE SE CREAN LOS FORMULARIOS A IMPLEMENTAR EN LOS FORMS PARA HACER SU REGISTROS EN LOS CAMPOS DE LOS ATRIBUTROS ASIGNADOS EN EL MODELO



####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################

from django import forms
from .models import Medicamento, Paciente, SalidaMedicamento, HistoriaMedica, Medico
from django.utils import timezone

class MedicamentoForm(forms.ModelForm):
    class Meta:
        model = Medicamento
        fields = ['clave', 'nombre', 'categoria', 'descripcion', 'fecha_caducidad', 'cantidad', 'status']
        widgets = {
            'clave': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fecha_caducidad': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        cantidad = cleaned_data.get('cantidad')
        fecha_caducidad = cleaned_data.get('fecha_caducidad')
        
        # Validar cantidad no negativa
        if cantidad is not None and cantidad < 0:
            self.add_error('cantidad', 'La cantidad no puede ser negativa')
        
        # Validar fecha de caducidad
        if fecha_caducidad and fecha_caducidad < timezone.now().date():
            self.add_error('fecha_caducidad', 'La fecha de caducidad no puede ser anterior a hoy')


class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['nombre', 'apellidos']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre')
        apellidos = cleaned_data.get('apellidos')
        
        # Validar que no haya números en nombre y apellidos
        if nombre and any(char.isdigit() for char in nombre):
            self.add_error('nombre', 'El nombre no puede contener números')
            
        if apellidos and any(char.isdigit() for char in apellidos):
            self.add_error('apellidos', 'Los apellidos no pueden contener números')

class SalidaMedicamentoForm(forms.ModelForm):
    class Meta:
        model = SalidaMedicamento
        fields = '__all__'
        widgets = {
            'medicamento': forms.Select(attrs={'class': 'form-control'}),
            'paciente': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'medico': forms.Select(attrs={'class': 'form-control'}),
        }


class HistoriaMedicaForm(forms.ModelForm):
    class Meta:
        model = HistoriaMedica
        fields = ['nota', 'medico']  # Añade el campo médico
        widgets = {
            'nota': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'medico': forms.Select(attrs={'class': 'form-control'}),
        }


class MedicoForm(forms.ModelForm):
    class Meta:
        model = Medico
        fields = ['nombre', 'apellidos', 'especialidad', 'telefono', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'especialidad': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre')
        apellidos = cleaned_data.get('apellidos')
        telefono = cleaned_data.get('telefono')
        
        # Validar nombre y apellidos
        if nombre and any(char.isdigit() for char in nombre):
            self.add_error('nombre', 'El nombre no puede contener números')
            
        if apellidos and any(char.isdigit() for char in apellidos):
            self.add_error('apellidos', 'Los apellidos no pueden contener números')
        
        # Validar teléfono
        if telefono and any(char.isalpha() for char in telefono):
            self.add_error('telefono', 'El teléfono solo puede contener números')