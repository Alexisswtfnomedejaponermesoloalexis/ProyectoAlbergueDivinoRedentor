####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################




# AQUÍ EN ADMIN SE DESARROLLAN MULTIPLES PROCESOS PARA LA ADMINISTRACIÓN DEL PANEL DE ADMIN DE DJANGO

# AQUÍ SE ADMINISTRA LAS CATEGORIAS DE LOS MEDICAMENTOS, LOS MEDICAMENTOS, LOS PACIENTES, LOS MÉDICOS ->
# LAS SALIDAS DE MEDICAMENTO Y LOS EXPEDIENTES DE OS PACIENTES

####################################################################################################################################################

# LA CLASE DE ADMINISTRAR_SALIDAS REALIZA EL PROCESO POR DECIRSE [COMPLEJO], YA QUE REALIZAR EL DESCUENTO->
# INMEDIATO EN LAS EXISTENCIAS REGISTRADAS EN MEDICAMENTO

# IMPLEMENTAMOS LA FORMA DE CONCATENACIÓN F.STRING 
# LA FORMA DE CONCATENAR DE RETURN('CAMPO1', 'CAMPO2') RETORNA UNA COLECCIÓN DE IDENTIFICADORES
# MIENTRAS QUE CON F.STRING CREA UN STRING PERSONALIZADO, COMBINA VALORES DE DIFERENTES CAMPOS U OBJETOS 
# ENTONCES, RESUMIENDO LO DICHO, USA COLECCIONES DE IDENTIFICADORES CUANDO NECESITES REFERIRTE A CAMPOS DEL MODELO
# MIENTRAS QUE F.STRING, LO PUEDES IMPLEMENTAR CUANDO NECESITES GENERAR TEXTO PERSONALIZADO PARA MOSTRAR UNA VISUALIZACIÓN

# NO QUIERE DECIR QUE UNA FORMA SEA MEJOR QUE OTRA, SIMPLEMENTE SON DOS CAMINOS DIFERENTES QUE LLEVAN A UN MISMO DESTINO.
# AMBAS SON SENCILLAS DE INTERPRETAR YA QUE OBJ. SE REFIERE AL OBJETO INSTANCIADO DENTRO DE LA CLASE EN LA QUE TE ENCUENTRAS



####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################


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
        
        #propósito de super().: Llama al método de la clase padre (admin.ModelForm en este caso).
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

    #self: referencia a la instancia actual (AdministrarSalidas)
    #obj: Instancia del modelo específico que se está manipulando (SalidaMedicamento)
    def medicamento_info(self, obj):
        return obj.medicamento.nombre
    medicamento_info.short_description = 'Medicamento'
    
    #self: referencia a la instancia actual (AdministrarSalidas)
    #obj: Instancia del modelo específico que se está manipulando (SalidaMedicamento)
    def paciente_info(self, obj):
        return f"{obj.paciente.nombre} {obj.paciente.apellidos}"
    paciente_info.short_description = 'Paciente'
    
    #self: referencia a la instancia actual (AdministrarSalidas)
    #obj: Instancia del modelo específico que se está manipulando (SalidaMedicamento)
    def medico_info(self, obj):
        return f"{obj.medico.nombre} {obj.medico.apellidos}"
    medico_info.short_description = 'Médico'
    
    #self: referencia a la instancia actual (AdministrarSalidas)
    #obj: Instancia del modelo específico que se está manipulando (SalidaMedicamento)

    def get_readonly_fields(self, request, obj=None):
        if request.user.groups.filter(name="Usuarios").exists():
            return ('medicamento', 'paciente', 'cantidad', 'fecha', 'medico')
        return ('fecha',)
    
    #self: referencia a la instancia actual (AdministrarSalidas)
    #request: Objeto HttpRequest que contiene toda la información de la solicitud HTTP
    #obj: Instancia del modelo específico que se está manipulando (SalidaMedicamento)
    #form: Instancia del formulario utilizado en la vista de administración
    #change: Booleano que indica si es una edición o creación
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
            #propósito de super().: Llama al método de la clase padre (admin.ModelAdmin en este caso).
            #save_model(): Guarda el objeto en la base de datos.
            #delete_model(): Elimina el objeto de la base de datos.
        super().save_model(request, obj, form, change)

     #self: referencia a la instancia actual (AdministrarSalidas)
    #request: Objeto HttpRequest que contiene toda la información de la solicitud HTTP
    #obj: Instancia del modelo específico que se está manipulando (SalidaMedicamento)
    def delete_model(self, request, obj):
        medicamento = obj.medicamento
        medicamento.cantidad += obj.cantidad
        medicamento.status = True
        medicamento.save()
        #propósito de super().: Llama al método de la clase padre (admin.ModelAdmin en este caso).
        #save_model(): Guarda el objeto en la base de datos.
        #delete_model(): Elimina el objeto de la base de datos.
        super().delete_model(request, obj)
        
admin.site.register(SalidaMedicamento, AdministrarSalidas)

# Vista personalizada para el admin
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