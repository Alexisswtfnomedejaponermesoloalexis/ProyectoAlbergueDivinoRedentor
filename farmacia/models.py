from django.db import models

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