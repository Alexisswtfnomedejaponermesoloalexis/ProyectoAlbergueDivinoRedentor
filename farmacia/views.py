####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################

# ESTE ES EL CEREBRO DE LA APLICACIÓN WEB, AQUÍ SE LLEVAN A ACABO TODOS LOS PROCESOS MENCIONADOS ANTERIORMENTE, DESDE DAR DE ALTA A UN PACIENTE, UNA SALIDA
# MEDICAMENTO, HASTA ELIMINAR O EDITAR SUS DATOS, DE IGUAL MANERA SE LLEVA EL CONTROL DEL EXPEDIENTE.

# TODA FUNCIÓN EXTRA QUE SE VAYA A AGREGAR A LA APLICAICÓN, DEBERÁ TENER SU FUNCIÓN EN ESTE DOCUMENTO PARA QUE ASÍ PUEDA FUNCIONAR DE MANERA ÓPTIMA.
# DEPENDIENDO DE LA FUNCIÓN QUE SE DESEE AGREGAR CAMBIARAN LOS PARÁMETROS O FUNCIONES A USAR.



####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from .models import CategoriaMedicamento, Medicamento, Paciente, ExpedienteMedico, SalidaMedicamento, Medico
from .forms import MedicamentoForm, PacienteForm, SalidaMedicamentoForm, HistoriaMedicaForm, MedicoForm

#FUNCIÓN DEL MENÚ PRINCIPAL, LA FUNCIÓN INDEX PERMITE MOSTRAR UNA INTERFAZ MÁS INTUITIVA MOSTRANDO CARDS DE INFORMACIÓN.
# PERMITE MOSTRAR LOS EL CONTEO D EMÉDICOS, PACIENTES, LOS MEDICAMENTOS_CRITICOS

def index(request):
    context = {
        'criticos_count': Medicamento.objects.filter(cantidad__lt=5).count(),
        'salidas_hoy_count': SalidaMedicamento.objects.count(),
        'pacientes_count': Paciente.objects.count(),
        'medicos_count': Medico.objects.count(),
        'ultimas_salidas': SalidaMedicamento.objects.select_related('medicamento', 'paciente', 'medico')[:5]
    }
    
    return render(request, 'index.html', context)

# FUNCIÓN PACIENTES, DICHA FUNCIÓN ALMACENA A LOS PACIENTES REGISTRADOS EN 'pacientes_list' ASIGNANDOLE LOS OBJETOS DADOS DE ALTA EN REFERENCIA AL MODELO 'Paciente'
# AL ÚTLIMO RETORNA LOS DATOS ALMACENADOS A SU RESPECTIVA VISTA (EN ESTE CASO ES "pacientes.html")

def pacientes(request):
    pacientes_list = Paciente.objects.all()
    context = {
        'pacientes': pacientes_list
    }
    return render(request, 'pacientes.html', context)

# FUNCIÓN MÉDICOS, ESTA FUNCIÓN SIRVE PARA ALMACENAR A LOS MÉDICOS REGISTRADOS EN "medicos_list" ASIGNANDOLE LOS OBJETOS DADOS DE ALTA EN REFERENCIA AL MODELO 'médico
# AL ÚTLIMO RETORNA LOS DATOS ALMACENADOS A SU RESPECTIVA VISTA (EN ESTE CASO ES "medicos.html")


def medicos(request):
    medicos_list = Medico.objects.all()
    context = {
        'medicos': medicos_list
    }
    return render(request, 'medicos.html', context)

# FUNCIÓN MEDICAMENTOS, AQUÍ SE REALIZA LOS EDITS PARA CONFIGURAR SOBRE LOS MEDICAMENTOS QUE SE ENCUENTRAN EN INVENTARIO CRÍTICO, MEDIANTE EL (.filter(cantidad__5))
# AL IGUAL QUE SE SELECCIONA LA CATEGORIA (DICHAS CATEGORIAS SE ASIGNAN DIRECTAMENTE EN EL PANEL DEL ADMINISTRADOR)

def medicamentos(request):
    medicamentos_list = Medicamento.objects.select_related('categoria').all()
    criticos = Medicamento.objects.filter(cantidad__lt=5)
    categorias = CategoriaMedicamento.objects.all()
    
    context = {
        'medicamentos': medicamentos_list,
        'criticos': criticos,
        'categorias': categorias
    }
    return render(request, 'medicamentos.html', context)

# FUNCIÓN DE SALIDAS, AQUÍ SE RELACIONA CON EL MODELO 'SalidaMedicamento' 
# AQUÍ MUESTRA LAS SALIDAS REGISTRADAS CON ANTERIORIRDAD, MOSTRANDO EL MÉDICO, PACIENTE Y MEDICAMENTO ASIGNADO

def salidas(request):
    salidas_list = SalidaMedicamento.objects.select_related('medicamento', 'paciente', 'medico').all()
    context = {
        'salidas': salidas_list
    }
    return render(request, 'salidas.html', context)

# FUNCIÓN DE REPORTES, *MÓDUCLO AÚN SIN TÉRMINAR*
# AQUÍ HACEMOS USO DEL MÉTODO .ANNOTATE()
# DICHO MÉTODO SE UTILIZA PARA REALIZAR AGREGACIONES Y CÁLCULOS SOBRE GRUPOS DE REGISTROS EN ESTE CASO A 'cantidad'
# SE REQUIERE IMPORTAR 'SUM'
# EL MÉTODO DE ORDER_BY SIRVE PARA ORDENAR LOS VALORES
def reportes(request):
    # Estadísticas de medicamentos más entregados
    medicamentos_mas_entregados = SalidaMedicamento.objects.values(
        'medicamento__nombre'
    ).annotate(
        total=Sum('cantidad')
    ).order_by('-total')[:5]
    
    # AQUÍ ALMACENA LOS MEDICAMENTOS CRÍTICOS FILTRANDO SOLO LA CANTIDAD DE EXISTENCIAS __LT5
    medicamentos_criticos = Medicamento.objects.filter(cantidad__lt=5)
    
    ## MÓDULO DE REPORTES AÚN SIN TERMINAR

    context = {
        'medicamentos_mas_entregados': medicamentos_mas_entregados,
        'medicamentos_criticos': medicamentos_criticos
    }
    return render(request, 'reportes.html', context)


# FUNCIÓN DE EXPEDIENTES, DICHA FUNCIÓN DE EXPEDIENTE TRABAJA EN CONJUNTO CON 3 MODELOS, EXTRAE TODOS LOS DATOS DEL PACIENTE
# UTILIZA EL MODELO HISTOPRIA_MÉDICA, HISTORIA_MÉDICA FUNCIONA COMO NOTAS QUE AGREGA EL MÉDICO HACÍA EL PACIENTE
#  AL IGUAL QUE VÍNCULA LAS SALIDAS DE MEDICAMENTO QUE SE LE HAN ASIGNADO AL PACIENTE 


def expediente(request, id):
    paciente = get_object_or_404(Paciente, pk=id)
    expediente, created = ExpedienteMedico.objects.get_or_create(paciente=paciente)
    salidas = SalidaMedicamento.objects.filter(paciente=paciente).select_related('medicamento')
    
    # Obtener todas las historias médicas ordenadas por fecha descendente
    # HACEMOS USO DEL MÉTODO ==POST
    historias = expediente.historias.all().order_by('-fecha_creacion')
    
    if request.method == 'POST':
        form = HistoriaMedicaForm(request.POST)
        if form.is_valid():
            nueva_historia = form.save(commit=False)
            nueva_historia.expediente = expediente
            nueva_historia.save()
            messages.success(request, 'Nota médica agregada correctamente')
            return redirect('expediente', id=paciente.id)
    else:
        form = HistoriaMedicaForm()
    
    context = {
        'paciente': paciente,
        'expediente': expediente,
        'salidas': salidas,
        'historias': historias,
        'form': form
    }
    return render(request, 'expediente.html', context)


## F    O   R   M   S        AQUÍ SE ALMACENAN LAS FUNCIONES DE LOS FORMULARIOS DE AGREGAR UNA ALTA O EDITAR UNA ALTA REGISTRADA        ##


# FUNCIÓN MEDICAMENTO_NUEVO CUYA FUNCIÓN SIRVE PARA DAR DE ALTA MEDICAMENTOS
# HACEMOS USO DEL MÉTODO POST PARA HACE ENVÍO DE DATOS DEL FORMULARIO 

def medicamento_nuevo(request):
    if request.method == 'POST':
        # (request.POST) FORMULARIO CON DATOS RECIBIDOS
        form = MedicamentoForm(request.POST)
        # SE VALIDAN LOS DATOS
        if form.is_valid():
            #LOS GUARDA EN LA BDD
            form.save()
            messages.success(request, 'Medicamento creado correctamente')
            return redirect('medicamentos')
        
        #AQUÍ SE SOLICITA EL FORMULARIO VACÍO
    else:
        form = MedicamentoForm()
    
    context = {
        'titulo': 'Nuevo Medicamento',
        'form': form
    }
    return render(request, 'forms/medicamento_form.html', context)

# FUNCIÓN MEDICAMENTO_EDITAR, DICHA FUNCIÓN SIRVE PARA EDITAR LOS MEDCICAMENTOS REGISTRADOS
# HACEMOS USO DEL ('get_object_or_404' por si no identifica el medicamento, e sporque no esta registrado aún, o en sud efecto hay un error)
# SE IDENTIFICA MEDIANTE LA PK=PRIMARY KEY QUE EN ESTE CASO ES EL ID DEL MEDICAMENTO

def medicamento_editar(request, id):
    medicamento = get_object_or_404(Medicamento, pk=id)
    
    #AQUÍ SE ENVÍA LOS DATOS EDITADOS
    if request.method == 'POST':
        #FORMULARIO DE DATOS (MEDICAMENTO FORM) CON LA INSTANCIA EXISTENTE (OBJ.MEDICAMENTO)
        form = MedicamentoForm(request.POST, instance=medicamento)
        if form.is_valid():
            # ACTUALIZA EL REGISTRO EXISTENTE
            form.save()
            messages.success(request, 'Medicamento actualizado correctamente')
            return redirect('medicamentos')
        # SOLICITUD PARA EDITAR
    else:
        #SE PRECARGA EL FORMULARIO CON LOS DATOS EXISTENTES
        form = MedicamentoForm(instance=medicamento)
    
    context = {
        'titulo': 'Editar Medicamento',
        'form': form,
        'medicamento': medicamento
    }
    return render(request, 'forms/medicamento_form.html', context)

def paciente_nuevo(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paciente creado correctamente')
            return redirect('pacientes')
    else:
        form = PacienteForm()
    
    context = {
        'titulo': 'Nuevo Paciente',
        'form': form
    }
    return render(request, 'forms/paciente_form.html', context)

def paciente_editar(request, id):
    paciente = get_object_or_404(Paciente, pk=id)
    
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paciente actualizado correctamente')
            return redirect('pacientes')
    else:
        form = PacienteForm(instance=paciente)
    
    context = {
        'titulo': 'Editar Paciente',
        'form': form
    }
    return render(request, 'forms/paciente_form.html', context)

def salida_nueva(request):
    if request.method == 'POST':
        form = SalidaMedicamentoForm(request.POST)
        if form.is_valid():
            salida = form.save()
            # Actualizar inventario
            medicamento = salida.medicamento
            medicamento.cantidad -= salida.cantidad
            if medicamento.cantidad < 0:
                medicamento.cantidad = 0
            medicamento.save()
            messages.success(request, 'Salida registrada correctamente')
            return redirect('salidas')
    else:
        form = SalidaMedicamentoForm()
    
    context = {
        'titulo': 'Nueva Salida de Medicamento',
        'form': form
    }
    return render(request, 'forms/salida_form.html', context)

def medico_nuevo(request):
    if request.method == 'POST':
        form = MedicoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Médico creado correctamente')
            return redirect('medicos')
    else:
        form = MedicoForm()
    
    context = {
        'titulo': 'Nuevo Médico',
        'form': form
    }
    return render(request, 'forms/medico_form.html', context)

def medico_editar(request, id):
    medico = get_object_or_404(Medico, pk=id)
    
    if request.method == 'POST':
        form = MedicoForm(request.POST, instance=medico)
        if form.is_valid():
            form.save()
            messages.success(request, 'Médico actualizado correctamente')
            return redirect('medicos')
    else:
        form = MedicoForm(instance=medico)
    
    context = {
        'titulo': 'Editar Médico',
        'form': form,
        'medico': medico
    }
    return render(request, 'forms/medico_form.html', context)

#DELETE
def medicamento_eliminar(request, id):
    medicamento = get_object_or_404(Medicamento, pk=id)
    
    if request.method == 'POST':
        medicamento.delete()
        messages.success(request, 'Medicamento eliminado correctamente')
        return redirect('medicamentos')
    
    context = {
        'medicamento': medicamento
    }
    return render(request, 'delete/medicamento_eliminar.html', context)

def paciente_eliminar(request, id):
    paciente = get_object_or_404(Paciente, pk=id)
    
    if request.method == 'POST':
        paciente.delete()
        messages.success(request, 'Paciente eliminado correctamente')
        return redirect('pacientes')
    
    context = {
        'paciente': paciente
    }
    return render(request, 'delete/paciente_eliminar.html', context)

def medico_eliminar(request, id):
    medico = get_object_or_404(Medico, pk=id)
    
    if request.method == 'POST':
        medico.delete()
        messages.success(request, 'Médico eliminado correctamente')
        return redirect('medicos')
    
    context = {
        'medico': medico
    }
    return render(request, 'delete/medico_eliminar.html', context)

