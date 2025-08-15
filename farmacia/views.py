####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################
####################################################################################################################################################

# ESTE ES EL CEREBRO DE LA APLICACIÓN WEB, AQUÍ SE LLEVAN A CABO TODOS LOS PROCESOS MENCIONADOS ANTERIORMENTE, DESDE DAR DE ALTA A UN PACIENTE, UNA SALIDA
# MEDICAMENTO, HASTA ELIMINAR O EDITAR SUS DATOS, DE IGUAL MANERA SE LLEVA EL CONTROL DEL EXPEDIENTE.

# TODA FUNCIÓN EXTRA QUE SE VAYA A AGREGAR A LA APLICACIÓN, DEBERÁ TENER SU FUNCIÓN EN ESTE DOCUMENTO PARA QUE ASÍ PUEDA FUNCIONAR DE MANERA ÓPTIMA.
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
from django.db.models import Count
import json
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from django.utils import timezone


# Vista principal (dashboard)
def index(request):
    """
    Muestra la página principal del sistema con estadísticas resumidas:
    - Conteo de medicamentos críticos (menos de 5 unidades)
    - Conteo de salidas de medicamentos registradas hoy
    - Conteo total de pacientes
    - Conteo total de médicos
    - Últimas 5 salidas de medicamentos
    """
    context = {
        'criticos_count': Medicamento.objects.filter(cantidad__lt=5).count(),
        'salidas_hoy_count': SalidaMedicamento.objects.count(),
        'pacientes_count': Paciente.objects.count(),
        'medicos_count': Medico.objects.count(),
        'ultimas_salidas': SalidaMedicamento.objects.select_related('medicamento', 'paciente', 'medico')[:5]
    }
    
    return render(request, 'index.html', context)

# Vista para listar pacientes
def pacientes(request):
    """
    Muestra todos los pacientes registrados en el sistema.
    Obtiene la lista completa de pacientes desde la base de datos.
    """
    pacientes_list = Paciente.objects.all()
    context = {
        'pacientes': pacientes_list
    }
    return render(request, 'pacientes.html', context)

# Vista para listar médicos
def medicos(request):
    """
    Muestra todos los médicos registrados en el sistema.
    Obtiene la lista completa de médicos desde la base de datos.
    """
    medicos_list = Medico.objects.all()
    context = {
        'medicos': medicos_list
    }
    return render(request, 'medicos.html', context)

# Vista para listar medicamentos
def medicamentos(request):
    """
    Muestra el inventario completo de medicamentos con:
    - Lista de todos los medicamentos con su categoría
    - Medicamentos en estado crítico (menos de 5 unidades)
    - Todas las categorías disponibles para filtrado
    """
    # Obtener todos los medicamentos con su categoría relacionada
    medicamentos_list = Medicamento.objects.select_related('categoria').all()
    
    # Filtrar medicamentos críticos (menos de 5 unidades)
    criticos = Medicamento.objects.filter(cantidad__lt=5)
    
    # Obtener todas las categorías para el filtro
    categorias = CategoriaMedicamento.objects.all()
    
    context = {
        'medicamentos': medicamentos_list,
        'criticos': criticos,
        'categorias': categorias
    }
    return render(request, 'medicamentos.html', context)

# Vista para listar salidas de medicamentos
def salidas(request):
    """
    Muestra todas las salidas de medicamentos registradas.
    Incluye información relacionada de medicamento, paciente y médico.
    """
    salidas_list = SalidaMedicamento.objects.select_related('medicamento', 'paciente', 'medico').all()
    context = {
        'salidas': salidas_list
    }
    return render(request, 'salidas.html', context)

# Vista de reportes y estadísticas
def reportes(request):
    """
    Genera reportes y estadísticas del sistema:
    - Top 5 de medicamentos más entregados
    - Medicamentos en estado crítico (menos de 5 unidades)
    - Datos para gráficas de medicamentos entregados y distribución por categoría
    """
    # Estadísticas de medicamentos más entregados (top 5)
    medicamentos_mas_entregados = SalidaMedicamento.objects.values(
        'medicamento__nombre'
    ).annotate(
        total=Sum('cantidad')
    ).order_by('-total')[:5]
    
    # Medicamentos críticos (menos de 5 unidades)
    medicamentos_criticos = Medicamento.objects.filter(cantidad__lt=5)
    
    # Datos para gráfica de medicamentos más entregados
    medicamentos_entregados_data = list(
        SalidaMedicamento.objects.values('medicamento__nombre')
        .annotate(total=Sum('cantidad'))
        .order_by('-total')[:5]
    )
    
    # Datos para gráfica de distribución por categoría
    distribucion_categorias = list(
        Medicamento.objects.values('categoria__nombre')
        .annotate(total=Sum('cantidad'))
        .exclude(total=0)
    )
    
    # Convertir datos a JSON para usar en JavaScript (gráficas)
    medicamentos_entregados_json = json.dumps(
        [{'medicamento': item['medicamento__nombre'], 'total': item['total']} 
         for item in medicamentos_entregados_data]
    )
    
    distribucion_categorias_json = json.dumps(
        [{'categoria': item['categoria__nombre'], 'total': item['total']} 
         for item in distribucion_categorias]
    )
    
    context = {
        'medicamentos_mas_entregados': medicamentos_mas_entregados,
        'medicamentos_criticos': medicamentos_criticos,
        'medicamentos_entregados_json': medicamentos_entregados_json,
        'distribucion_categorias_json': distribucion_categorias_json
    }
    return render(request, 'reportes.html', context)

# Vista para ver y gestionar expediente médico de un paciente
def expediente(request, id):
    """
    Muestra y gestiona el expediente médico de un paciente específico:
    - Información básica del paciente
    - Historial médico (notas médicas)
    - Salidas de medicamentos asociadas al paciente
    
    Permite agregar nuevas notas médicas al expediente.
    """
    # Obtener paciente por ID o mostrar error 404 si no existe
    paciente = get_object_or_404(Paciente, pk=id)
    
    # Obtener o crear expediente médico del paciente
    expediente, created = ExpedienteMedico.objects.get_or_create(paciente=paciente)
    
    # Obtener salidas de medicamento asociadas al paciente
    salidas = SalidaMedicamento.objects.filter(paciente=paciente).select_related('medicamento')
    
    # Obtener historias médicas ordenadas por fecha (más reciente primero)
    historias = expediente.historias.all().order_by('-fecha_creacion')
    
    # Procesar formulario para nueva historia médica
    if request.method == 'POST':
        form = HistoriaMedicaForm(request.POST)
        if form.is_valid():
            # Crear nueva historia médica sin guardar aún
            nueva_historia = form.save(commit=False)
            # Asociar al expediente del paciente
            nueva_historia.expediente = expediente
            # Guardar en base de datos
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

######################################################################################
### FORMULARIOS - FUNCIONES PARA CREAR Y EDITAR REGISTROS EN EL SISTEMA ###
######################################################################################

# Crear nuevo medicamento
def medicamento_nuevo(request):
    """
    Maneja la creación de nuevos medicamentos en el sistema:
    - Muestra formulario vacío para nuevo medicamento (GET)
    - Procesa formulario enviado y guarda en base de datos (POST)
    - Muestra mensajes de éxito o error
    """
    if request.method == 'POST':
        # Procesar formulario con datos recibidos
        form = MedicamentoForm(request.POST)
        if form.is_valid():
            # Guardar medicamento en base de datos
            form.save()
            messages.success(request, 'Medicamento creado correctamente')
            return redirect('medicamentos')
    else:
        # Mostrar formulario vacío para nuevo medicamento
        form = MedicamentoForm()
    
    context = {
        'titulo': 'Nuevo Medicamento',
        'form': form
    }
    return render(request, 'forms/medicamento_form.html', context)

# Editar medicamento existente
def medicamento_editar(request, id):
    """
    Maneja la edición de medicamentos existentes:
    - Obtiene medicamento por ID o muestra error 404
    - Muestra formulario precargado con datos actuales (GET)
    - Procesa formulario enviado y actualiza en base de datos (POST)
    """
    # Obtener medicamento o mostrar error 404
    medicamento = get_object_or_404(Medicamento, pk=id)
    
    if request.method == 'POST':
        # Procesar formulario con datos actualizados
        form = MedicamentoForm(request.POST, instance=medicamento)
        if form.is_valid():
            # Actualizar medicamento en base de datos
            form.save()
            messages.success(request, 'Medicamento actualizado correctamente')
            return redirect('medicamentos')
    else:
        # Mostrar formulario con datos actuales del medicamento
        form = MedicamentoForm(instance=medicamento)
    
    context = {
        'titulo': 'Editar Medicamento',
        'form': form,
        'medicamento': medicamento
    }
    return render(request, 'forms/medicamento_form.html', context)

# Crear nuevo paciente
def paciente_nuevo(request):
    """
    Maneja la creación de nuevos pacientes en el sistema.
    Similar a medicamento_nuevo pero para pacientes.
    """
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

# Editar paciente existente
def paciente_editar(request, id):
    """
    Maneja la edición de pacientes existentes.
    Similar a medicamento_editar pero para pacientes.
    """
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

# Registrar nueva salida de medicamento
def salida_nueva(request):
    """
    Maneja el registro de nuevas salidas de medicamentos:
    - Procesa formulario y registra la salida (POST)
    - Actualiza el inventario del medicamento
    - Maneja casos donde no hay suficiente inventario
    """
    if request.method == 'POST':
        form = SalidaMedicamentoForm(request.POST)
        if form.is_valid():
            # Guardar salida sin actualizar inventario aún
            salida = form.save(commit=False)
            
            # Actualizar inventario del medicamento
            medicamento = salida.medicamento
            medicamento.cantidad -= salida.cantidad
            
            # Prevenir cantidades negativas
            if medicamento.cantidad < 0:
                medicamento.cantidad = 0
            
            # Actualizar estado del medicamento
            medicamento.status = medicamento.cantidad > 0
            medicamento.save()
            
            # Guardar salida definitivamente
            salida.save()
            
            messages.success(request, 'Salida registrada correctamente')
            return redirect('salidas')
    else:
        form = SalidaMedicamentoForm()
    
    context = {
        'titulo': 'Nueva Salida de Medicamento',
        'form': form
    }
    return render(request, 'forms/salida_form.html', context)

# Crear nuevo médico
def medico_nuevo(request):
    """
    Maneja la creación de nuevos médicos en el sistema.
    Similar a paciente_nuevo pero para médicos.
    """
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

# Editar médico existente
def medico_editar(request, id):
    """
    Maneja la edición de médicos existentes.
    Similar a paciente_editar pero para médicos.
    """
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

######################################################################################
### ELIMINACIONES - FUNCIONES PARA ELIMINAR REGISTROS DEL SISTEMA ###
######################################################################################

# Eliminar medicamento
def medicamento_eliminar(request, id):
    """
    Maneja la eliminación de medicamentos:
    - Confirma la eliminación (GET)
    - Elimina el medicamento de la base de datos (POST)
    """
    medicamento = get_object_or_404(Medicamento, pk=id)
    
    if request.method == 'POST':
        medicamento.delete()
        messages.success(request, 'Medicamento eliminado correctamente')
        return redirect('medicamentos')
    
    context = {
        'medicamento': medicamento
    }
    return render(request, 'delete/medicamento_eliminar.html', context)

# Eliminar paciente
def paciente_eliminar(request, id):
    """
    Maneja la eliminación de pacientes.
    Similar a medicamento_eliminar pero para pacientes.
    """
    paciente = get_object_or_404(Paciente, pk=id)
    
    if request.method == 'POST':
        paciente.delete()
        messages.success(request, 'Paciente eliminado correctamente')
        return redirect('pacientes')
    
    context = {
        'paciente': paciente
    }
    return render(request, 'delete/paciente_eliminar.html', context)

# Eliminar médico
def medico_eliminar(request, id):
    """
    Maneja la eliminación de médicos.
    Similar a medicamento_eliminar pero para médicos.
    """
    medico = get_object_or_404(Medico, pk=id)
    
    if request.method == 'POST':
        medico.delete()
        messages.success(request, 'Médico eliminado correctamente')
        return redirect('medicos')
    
    context = {
        'medico': medico
    }
    return render(request, 'delete/medico_eliminar.html', context)

######################################################################################
### FUNCIONES ESPECIALES - REPORTES PDF, CATEGORÍAS, ETC. ###
######################################################################################

# Generar PDF de inventario
def generar_pdf_inventario(request):
    """
    Genera un reporte PDF del inventario de medicamentos:
    - Lista completa de medicamentos con sus detalles
    - Sección especial para medicamentos críticos
    - Diseño profesional con estilos y colores
    """
    # Obtener todos los medicamentos con sus categorías
    medicamentos = Medicamento.objects.select_related('categoria').all()
    
    # Configurar respuesta HTTP para PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="inventario_medicamentos.pdf"'
    
    # Crear buffer para el PDF
    buffer = BytesIO()
    
    # Configurar documento PDF en formato horizontal
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    elements = []
    
    # Estilos para el documento
    styles = getSampleStyleSheet()
    style_title = styles['Title']
    style_heading = styles['Heading2']
    style_body = styles['BodyText']
    
    # Título del documento
    elements.append(Paragraph("Inventario de Medicamentos - Albergue Divino Redentor", style_title))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Fecha de generación: {timezone.now().strftime('%d/%m/%Y %H:%M')}", style_body))
    elements.append(Spacer(1, 24))
    
    # Preparar datos para la tabla principal
    data = [["Clave", "Nombre", "Categoría", "Descripción", "Existencias", "Estado", "Caducidad"]]
    
    for med in medicamentos:
        # Determinar estado (Disponible/No disponible)
        estado = "Disponible" if med.status else "No disponible"
        
        # Formatear fecha de caducidad
        caducidad = med.fecha_caducidad.strftime("%d/%m/%Y") if med.fecha_caducidad else "N/A"
        
        # Acortar descripción si es muy larga
        descripcion = (med.descripcion[:50] + '...') if med.descripcion and len(med.descripcion) > 50 else med.descripcion or ""
        
        # Agregar fila a la tabla
        data.append([
            med.clave,
            med.nombre,
            med.categoria.nombre,
            descripcion,
            str(med.cantidad),
            estado,
            caducidad
        ])
    
    # Crear tabla principal
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0d6efd')),  # Encabezado azul
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),            # Texto blanco encabezado
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),                        # Centrar todo el contenido
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),              # Negrita encabezado
        ('FONTSIZE', (0,0), (-1,0), 12),                            # Tamaño fuente encabezado
        ('BOTTOMPADDING', (0,0), (-1,0), 12),                       # Espaciado inferior encabezado
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f8f9fa')), # Fondo gris claro para filas
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#dee2e6')),    # Bordes grises
        ('FONTSIZE', (0,1), (-1,-1), 10),                           # Tamaño fuente contenido
    ]))
    
    # Resaltar medicamentos críticos (menos de 5 unidades)
    for i in range(1, len(data)):
        if int(data[i][4]) < 5:  # Columna de existencias
            table.setStyle(TableStyle([
                ('TEXTCOLOR', (0,i), (-1,i), colors.red),           # Texto rojo
                ('FONTNAME', (0,i), (-1,i), 'Helvetica-Bold'),      # Negrita
            ]))
    
    elements.append(table)
    
    # Sección adicional para medicamentos críticos
    criticos = Medicamento.objects.filter(cantidad__lt=5)
    if criticos.exists():
        elements.append(Spacer(1, 24))
        elements.append(Paragraph("Medicamentos Críticos (menos de 5 unidades)", style_heading))
        elements.append(Spacer(1, 12))
        
        # Preparar datos para tabla de críticos
        crit_data = [["Nombre", "Categoría", "Existencias", "Caducidad"]]
        for med in criticos:
            caducidad = med.fecha_caducidad.strftime("%d/%m/%Y") if med.fecha_caducidad else "N/A"
            crit_data.append([med.nombre, med.categoria.nombre, str(med.cantidad), caducidad])
        
        # Crear tabla de críticos
        crit_table = Table(crit_data)
        crit_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#dc3545')), # Encabezado rojo
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),           # Texto blanco encabezado
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),                       # Centrar contenido
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),             # Negrita encabezado
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#fff3cd')),# Fondo amarillo claro
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#dc3545')),   # Bordes rojos
            ('TEXTCOLOR', (0,1), (-1,-1), colors.HexColor('#dc3545')), # Texto rojo
        ]))
        elements.append(crit_table)
    
    # Construir el PDF
    doc.build(elements)
    
    # Obtener PDF del buffer y enviar como respuesta
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response

# Crear nueva categoría de medicamento
def categoria_nueva(request):
    """
    Maneja la creación de nuevas categorías de medicamentos:
    - Recibe el nombre de la categoría por POST
    - Crea la categoría en la base de datos
    - Muestra mensajes de éxito o error
    """
    if request.method == 'POST':
        # Obtener nombre de categoría del formulario
        nombre = request.POST.get('nombre')
        if nombre:
            # Crear y guardar nueva categoría
            CategoriaMedicamento.objects.create(nombre=nombre)
            messages.success(request, 'Categoría creada correctamente')
            return redirect('medicamentos')
        else:
            # Mostrar error si no se proporcionó nombre
            messages.error(request, 'El nombre de la categoría es requerido')
    
    # Mostrar formulario para nueva categoría
    return render(request, 'forms/categoria_form.html')