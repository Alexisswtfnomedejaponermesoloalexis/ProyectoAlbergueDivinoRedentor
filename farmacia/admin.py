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

