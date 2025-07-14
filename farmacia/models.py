from django.db import models
from django.db import models
from django.core.exceptions import ValidationError
# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class CategoriaMedicamento(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Categoría de Medicamento"
        verbose_name_plural = "Categorías de Medicamentos"

    def _str_(self):
        return self.nombre
    
class Medicamento(models.Model):
    id = models.AutoField(primary_key=True)
    clave = models.CharField(max_length=50, unique=True, verbose_name="Clave única")
    nombre = models.CharField(max_length=200, verbose_name="Nombre")
    categoria = models.ForeignKey('CategoriaMedicamento', on_delete=models.CASCADE)
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    fecha_caducidad = models.DateField(verbose_name="Fecha de caducidad")
    cantidad = models.IntegerField(default=0, verbose_name="Cantidad en inventario")
    status = models.BooleanField(default=True, verbose_name="Disponible")

    class Meta:
        verbose_name = "Medicamento"
        verbose_name_plural = "Medicamentos"
        ordering = ['nombre']

    def _str_(self):
        return self.nombre

    def clean(self):
        """Validación simple para evitar cantidades negativas"""
        if self.cantidad < 0:
            raise ValidationError("La cantidad no puede ser negativa")
        
        # Si la cantidad es 0, marcar como no disponible
        if self.cantidad == 0:
            self.status = False
        else:
            self.status = True

class Paciente(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    apellidos = models.CharField(max_length=200)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"

    def __str__(self):
        return f"{self.nombre} {self.apellidos}"
    

class ExpedienteMedico(models.Model):
    id = models.AutoField(primary_key=True)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    historia_medica = models.TextField(blank=True, verbose_name="Historia Médica")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Expediente Médico"
        verbose_name_plural = "Expedientes Médicos"

    def _str_(self):
        return f"Expediente #{self.id} - {self.paciente.nombre}"
