from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.urls import path
from django.shortcuts import render
from django.utils import timezone
from .models import CategoriaMedicamento, Medicamento, Paciente, ExpedienteMedico, SalidaMedicamento, Medico

# Personalización avanzada del sitio admin
admin.site.site_header = "Administración del Albergue Divino Redentor"
admin.site.site_title = "Sistema de Farmacia"
admin.site.index_title = "Panel de Control"

class AdministrarCategorias(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)
    ordering = ['nombre']
    list_per_page = 20
    
    def get_readonly_fields(self, request, obj=None):
        if request.user.groups.filter(name="Usuarios").exists():
            return ('id',)
        return ()
admin.site.register(CategoriaMedicamento, AdministrarCategorias)

class AdministrarMedicamentos(admin.ModelAdmin):
    list_display = ('clave', 'nombre', 'categoria', 'cantidad', 'estado', 'fecha_caducidad')
    search_fields = ('clave', 'nombre', 'categoria__nombre')
    list_filter = ('categoria', 'status')
    date_hierarchy = 'fecha_caducidad'
    ordering = ['nombre']
    list_per_page = 20
    list_editable = ('cantidad',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('clave', 'nombre', 'categoria', 'descripcion')
        }),
        ('Inventario', {
            'fields': ('cantidad', 'fecha_caducidad', 'status'),
            'classes': ('collapse',)
        }),
    )
    
    def estado(self, obj):
        if obj.status:
            return "Disponible"
        else:
            return "No disponible"
    estado.short_description = 'Estado'
    
    def get_readonly_fields(self, request, obj=None):
        if request.user.groups.filter(name="Usuarios").exists():
            return ('clave', 'nombre', 'categoria', 'descripcion', 'fecha_caducidad', 'cantidad', 'status')
        return ()
admin.site.register(Medicamento, AdministrarMedicamentos)

class AdministrarMedicos(admin.ModelAdmin):
    list_display = ('id', 'nombre_completo', 'especialidad', 'telefono', 'activo')
    search_fields = ('nombre', 'apellidos', 'especialidad')
    list_filter = ('activo',)
    list_per_page = 20
    
    def nombre_completo(self, obj):
        return f"{obj.nombre} {obj.apellidos}"
    nombre_completo.short_description = 'Nombre Completo'

admin.site.register(Medico, AdministrarMedicos)

class AdministrarPacientes(admin.ModelAdmin):
    list_display = ('id', 'nombre_completo', 'fecha_registro')
    search_fields = ('nombre', 'apellidos')
    date_hierarchy = 'fecha_registro'
    ordering = ['apellidos', 'nombre']
    list_per_page = 20
    
    def nombre_completo(self, obj):
        return f"{obj.nombre} {obj.apellidos}"
    nombre_completo.short_description = 'Nombre Completo'
    
    def get_readonly_fields(self, request, obj=None):
        if request.user.groups.filter(name="Usuarios").exists():
            return ('id', 'nombre', 'apellidos', 'fecha_registro')
        return ()
admin.site.register(Paciente, AdministrarPacientes)

class AdministrarExpedientes(admin.ModelAdmin):
    list_display = ('id', 'paciente_info', 'fecha_creacion')
    search_fields = ('paciente__nombre', 'paciente__apellidos')
    date_hierarchy = 'fecha_creacion'
    list_per_page = 20
    
    def paciente_info(self, obj):
        return f"{obj.paciente.nombre} {obj.paciente.apellidos}"
    paciente_info.short_description = 'Paciente'
    
    def get_readonly_fields(self, request, obj=None):
        if request.user.groups.filter(name="Usuarios").exists():
            return ('paciente', 'historia_medica')
        return ()
admin.site.register(ExpedienteMedico, AdministrarExpedientes)

class SalidaMedicamentoForm(forms.ModelForm):
    class Meta:
        model = SalidaMedicamento
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super().clean()
        medicamento = cleaned_data.get('medicamento')
        cantidad = cleaned_data.get('cantidad')
        
        if not medicamento or not cantidad:
            return cleaned_data
        
        if self.instance.pk is None:
            if cantidad > medicamento.cantidad:
                mensaje = f"No hay suficiente inventario. Disponible: {medicamento.cantidad}"
                raise ValidationError(mensaje)
        else:
            salida_original = SalidaMedicamento.objects.get(pk=self.instance.pk)
            diferencia = cantidad - salida_original.cantidad
            disponible = medicamento.cantidad + salida_original.cantidad
            
            if diferencia > disponible:
                mensaje = f"No hay suficiente inventario. Disponible: {disponible}"
                raise ValidationError(mensaje)
        
        return cleaned_data


class AdministrarSalidas(admin.ModelAdmin):
    form = SalidaMedicamentoForm
    list_display = ('id', 'medicamento_info', 'paciente_info', 'cantidad', 'fecha', 'medico_info')
    search_fields = ('medicamento_nombre', 'pacientenombre', 'mediconombre', 'medico_apellidos')
    date_hierarchy = 'fecha'
    list_filter = ('medico',)
    list_per_page = 20
    
    def medicamento_info(self, obj):
        return obj.medicamento.nombre
    medicamento_info.short_description = 'Medicamento'
    
    def paciente_info(self, obj):
        return f"{obj.paciente.nombre} {obj.paciente.apellidos}"
    paciente_info.short_description = 'Paciente'
    
    def medico_info(self, obj):
        return f"{obj.medico.nombre} {obj.medico.apellidos}"
    medico_info.short_description = 'Médico'
    
    def get_readonly_fields(self, request, obj=None):
        if request.user.groups.filter(name="Usuarios").exists():
            return ('medicamento', 'paciente', 'cantidad', 'fecha', 'medico')
        return ('fecha',)
    
    def save_model(self, request, obj, form, change):
        if not change:
            medicamento = obj.medicamento
            medicamento.cantidad -= obj.cantidad
            if medicamento.cantidad < 0:
                medicamento.cantidad = 0
            medicamento.status = medicamento.cantidad > 0
            medicamento.save()
        else:
            salida_original = SalidaMedicamento.objects.get(pk=obj.pk)
            diferencia = obj.cantidad - salida_original.cantidad
            medicamento = obj.medicamento
            medicamento.cantidad -= diferencia
            if medicamento.cantidad < 0:
                medicamento.cantidad = 0
            medicamento.status = medicamento.cantidad > 0
            medicamento.save()
        super().save_model(request, obj, form, change)
    
    def delete_model(self, request, obj):
        medicamento = obj.medicamento
        medicamento.cantidad += obj.cantidad
        medicamento.status = True
        medicamento.save()
        super().delete_model(request, obj)
        
admin.site.register(SalidaMedicamento, AdministrarSalidas)

# Vista personalizada para el dashboard
def custom_dashboard(request):
    today = timezone.now().date()
    context = {
        'medicamentos_criticos': Medicamento.objects.filter(cantidad__lt=5),
        'salidas_hoy': SalidaMedicamento.objects.filter(fecha__date=today),
        'total_pacientes': Paciente.objects.count(),
        'total_medicos': Medico.objects.count(),
        'ultimas_salidas': SalidaMedicamento.objects.select_related(
            'medicamento', 'paciente', 'medico'
        ).order_by('-fecha')[:10],
        'today': today,
    }
    return render(request, 'admin/custom_dashboard.html', context)


# Añadir vista personalizada al admin
admin.site.index_template = 'custom_dashboard.html'