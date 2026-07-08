from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from .models import SolicitudCompra, ItemSolicitud, Proveedor, SolicitudCotizacion, Cotizacion, OrdenCompra, RecepcionMercancia, ItemRecepcion, Auditoria
from .forms import SolicitudCompraForm, ItemSolicitudFormSet, ProveedorForm, CotizacionForm
from .services import validar_disponibilidad_stock


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    error = None

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            error = "Usuario o contraseña incorrectos."

    return render(request, "login.html", {"error": error})


@login_required
def dashboard(request):

    if request.user.groups.filter(name="Administrador").exists():
        rol = "Administrador"

    elif request.user.groups.filter(name="Encargado de Compras").exists():
        rol = "Encargado de Compras"

    else:
        rol = "Sin rol"

    return render(
        request,
        "dashboard.html",
        {
            "rol": rol
        }
    )


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def usuarios(request):

    if not request.user.groups.filter(name="Administrador").exists():
        return HttpResponseForbidden("No tienes permisos para acceder a esta página.")

    return render(request, "usuarios.html")

# ST-2.4 Implementar registro de la solicitud
@login_required
def registrar_solicitud(request):
    if request.method == 'POST':
        form = SolicitudCompraForm(request.POST)
        formset = ItemSolicitudFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            solicitud = form.save(commit=False)
            solicitud.usuario = request.user
            solicitud.save()

            items = formset.save(commit=False)
            for item in items:
                item.solicitud = solicitud
                item.save()

            # ST-7.4
            Auditoria.objects.create(
                usuario=request.user,
                accion="Registro de Solicitud",
                detalle=f"Se registró la solicitud {solicitud.codigo}"
            )

            # ST-3.2, ST-3.3
            validar_disponibilidad_stock(solicitud)

            return redirect('listar_solicitudes')
    else:
        form = SolicitudCompraForm()
        formset = ItemSolicitudFormSet()

    return render(request, 'registrar_solicitud.html', {
        'form': form,
        'formset': formset
    })

# ST-2.5 Implementar consulta de solicitudes
@login_required
def listar_solicitudes(request):
    solicitudes = SolicitudCompra.objects.all().order_by('-fecha_registro')
    return render(request, 'listar_solicitudes.html', {'solicitudes': solicitudes})

# ST-2.6 Implementar edición de solicitudes
@login_required
def editar_solicitud(request, pk):
    solicitud = get_object_or_404(SolicitudCompra, pk=pk)

    if solicitud.estado not in ['Pendiente', 'En Revision']:
        return HttpResponseForbidden("No se puede editar una solicitud ya aprobada o rechazada.")

    if request.method == 'POST':
        form = SolicitudCompraForm(request.POST, instance=solicitud)
        formset = ItemSolicitudFormSet(request.POST, instance=solicitud)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('listar_solicitudes')
    else:
        form = SolicitudCompraForm(instance=solicitud)
        formset = ItemSolicitudFormSet(instance=solicitud)

    return render(request, 'editar_solicitud.html', {
        'form': form,
        'formset': formset,
        'solicitud': solicitud
    })

# ST-3.4 Crear bandeja de solicitudes pendientes
@login_required
def bandeja_pendientes(request):
    if not request.user.groups.filter(name__in=["Administrador", "Encargado de Compras"]).exists():
        return HttpResponseForbidden("No tienes permisos.")

    solicitudes = SolicitudCompra.objects.filter(estado='En Revision').order_by('-fecha_registro')
    return render(request, 'bandeja_pendientes.html', {'solicitudes': solicitudes})

# ST-3.5 Implementar aprobación de solicitudes
@login_required
def aprobar_solicitud(request, pk):
    if not request.user.groups.filter(name__in=["Administrador", "Encargado de Compras"]).exists():
        return HttpResponseForbidden("No tienes permisos.")

    solicitud = get_object_or_404(SolicitudCompra, pk=pk)
    solicitud.estado = 'Aprobada'
    solicitud.save()

    # ST-7.4
    Auditoria.objects.create(
        usuario=request.user,
        accion="Aprobación de Solicitud",
        detalle=f"Se aprobó la solicitud {solicitud.codigo}"
    )

    return redirect('bandeja_pendientes')

# ST-3.6 Implementar rechazo con justificación
@login_required
def rechazar_solicitud(request, pk):
    if not request.user.groups.filter(name__in=["Administrador", "Encargado de Compras"]).exists():
        return HttpResponseForbidden("No tienes permisos.")

    solicitud = get_object_or_404(SolicitudCompra, pk=pk)

    if request.method == 'POST':
        justificacion = request.POST.get('justificacion')
        if not justificacion:
            return render(request, 'rechazar_solicitud.html', {
                'solicitud': solicitud,
                'error': "La justificación es obligatoria."
            })
        solicitud.estado = 'Rechazada'
        solicitud.justificacion_rechazo = justificacion
        solicitud.save()
        return redirect('bandeja_pendientes')

    return render(request, 'rechazar_solicitud.html', {'solicitud': solicitud})

# ST-4.1 Registrar proveedores
@login_required
def registrar_proveedor(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_proveedores')
    else:
        form = ProveedorForm()
    return render(request, 'registrar_proveedor.html', {'form': form})

@login_required
def listar_proveedores(request):
    proveedores = Proveedor.objects.all()
    return render(request, 'listar_proveedores.html', {'proveedores': proveedores})

# ST-4.2 Registrar solicitud de cotización
# ST-4.3 Asociar proveedores a la solicitud
@login_required
def registrar_solicitud_cotizacion(request, solicitud_pk):
    solicitud_compra = get_object_or_404(SolicitudCompra, pk=solicitud_pk)

    if request.method == 'POST':
        proveedores_ids = request.POST.getlist('proveedores')
        if not proveedores_ids:
            return render(request, 'registrar_solicitud_cotizacion.html', {
                'solicitud_compra': solicitud_compra,
                'proveedores': Proveedor.objects.all(),
                'error': "Debe seleccionar al menos un proveedor."
            })

        sol_cot, created = SolicitudCotizacion.objects.get_or_create(solicitud_compra=solicitud_compra)
        sol_cot.proveedores.set(proveedores_ids)
        sol_cot.save()

        solicitud_compra.estado = 'Cotizada'
        solicitud_compra.save()

        return redirect('listar_solicitudes')

    proveedores = Proveedor.objects.all()
    return render(request, 'registrar_solicitud_cotizacion.html', {
        'solicitud_compra': solicitud_compra,
        'proveedores': proveedores
    })

# ST-4.4 Registrar precio unitario
# ST-4.5 Registrar tiempo de entrega y vigencia
@login_required
def registrar_cotizacion(request, sol_cot_pk):
    solicitud_cotizacion = get_object_or_404(SolicitudCotizacion, pk=sol_cot_pk)

    if request.method == 'POST':
        form = CotizacionForm(request.POST)
        if form.is_valid():
            cotizacion = form.save(commit=False)
            cotizacion.solicitud_cotizacion = solicitud_cotizacion
            cotizacion.save()
            return redirect('consultar_cotizaciones', sol_cot_pk=sol_cot_pk)
    else:
        form = CotizacionForm()
        # Limit providers to those associated with the request
        form.fields['proveedor'].queryset = solicitud_cotizacion.proveedores.all()

    return render(request, 'registrar_cotizacion.html', {
        'form': form,
        'solicitud_cotizacion': solicitud_cotizacion
    })

# ST-4.6 Consultar cotizaciones registradas
@login_required
def consultar_cotizaciones(request, sol_cot_pk):
    solicitud_cotizacion = get_object_or_404(SolicitudCotizacion, pk=sol_cot_pk)
    cotizaciones = solicitud_cotizacion.cotizaciones.all()
    return render(request, 'consultar_cotizaciones.html', {
        'solicitud_cotizacion': solicitud_cotizacion,
        'cotizaciones': cotizaciones
    })

# ST-5.1 Crear tabla comparativa de cotizaciones
@login_required
def comparar_cotizaciones(request, sol_cot_pk):
    solicitud_cotizacion = get_object_or_404(SolicitudCotizacion, pk=sol_cot_pk)
    cotizaciones = solicitud_cotizacion.cotizaciones.all().order_by('precio_unitario')
    return render(request, 'comparar_cotizaciones.html', {
        'solicitud_cotizacion': solicitud_cotizacion,
        'cotizaciones': cotizaciones
    })

# ST-5.2 Seleccionar cotización ganadora
# ST-5.3 Actualizar estado de las cotizaciones
@login_required
def seleccionar_ganador(request, cotizacion_pk):
    cotizacion_ganadora = get_object_or_404(Cotizacion, pk=cotizacion_pk)
    solicitud_cotizacion = cotizacion_ganadora.solicitud_cotizacion

    # Marcar esta como aceptada y las demás como rechazadas
    solicitud_cotizacion.cotizaciones.exclude(pk=cotizacion_pk).update(estado='Rechazada')
    cotizacion_ganadora.estado = 'Aceptada'
    cotizacion_ganadora.save()

    # Cambiar estado de la solicitud de compra
    solicitud_compra = solicitud_cotizacion.solicitud_compra
    solicitud_compra.estado = 'Orden Generada'
    solicitud_compra.save()

    # ST-5.4 Generar orden de compra automatically
    OrdenCompra.objects.create(cotizacion=cotizacion_ganadora)

    return redirect('listar_ordenes')

# ST-5.6 Consultar órdenes de compra
@login_required
def listar_ordenes(request):
    ordenes = OrdenCompra.objects.all().order_by('-fecha_generacion')
    return render(request, 'listar_ordenes.html', {'ordenes': ordenes})

# ST-6.1 Crear vista imprimible
# ST-6.2 Exportar orden a PDF
@login_required
def imprimir_orden(request, pk):
    orden = get_object_or_404(OrdenCompra, pk=pk)
    # Simple printable view, in a real scenario we might use a library like WeasyPrint
    # For now, we return a template optimized for print
    return render(request, 'imprimir_orden.html', {'orden': orden})

@login_required
def exportar_pdf_orden(request, pk):
    # Simulated PDF export
    from django.http import HttpResponse
    orden = get_object_or_404(OrdenCompra, pk=pk)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Orden_{orden.codigo}.pdf"'
    response.write(b"Contenido simulado de PDF para la orden " + orden.codigo.encode())
    return response

# ST-6.3 Mostrar órdenes pendientes
@login_required
def listar_ordenes_pendientes(request):
    ordenes = OrdenCompra.objects.filter(estado='Pendiente')
    return render(request, 'listar_ordenes_pendientes.html', {'ordenes': ordenes})

# ST-6.4 Registrar recepción de productos
# ST-6.5 Validar recepción contra la orden
# ST-6.6 Actualizar estado de recepción
@login_required
def registrar_recepcion(request, pk):
    orden = get_object_or_404(OrdenCompra, pk=pk)
    solicitud_compra = orden.cotizacion.solicitud_cotizacion.solicitud_compra
    items_solicitud = solicitud_compra.items.all()

    if request.method == 'POST':
        recepcion = RecepcionMercancia.objects.create(
            orden_compra=orden,
            observaciones=request.POST.get('observaciones')
        )

        diferencia_detectada = False
        for item in items_solicitud:
            cant_recibida = int(request.POST.get(f'cant_{item.pk}', 0))
            ItemRecepcion.objects.create(
                recepcion=recepcion,
                item_solicitud=item,
                cantidad_recibida=cant_recibida
            )

            if cant_recibida != item.cantidad:
                diferencia_detectada = True

        orden.estado = 'Recibida'
        orden.save()

        # ST-7.2 Cambiar estado de compra completada
        solicitud_compra.estado = 'Completada'
        solicitud_compra.save()

        # ST-7.4
        Auditoria.objects.create(
            usuario=request.user,
            accion="Recepción de Mercancía",
            detalle=f"Se recibió mercancía para la orden {orden.codigo}. Diferencias: {diferencia_detectada}"
        )

        # Sincronizar con logística
        from .services import actualizar_inventario
        for item_rec in recepcion.items.all():
            actualizar_inventario(item_rec.item_solicitud.producto, item_rec.cantidad_recibida)

        return render(request, 'recepcion_confirmada.html', {
            'recepcion': recepcion,
            'diferencia': diferencia_detectada
        })

    return render(request, 'registrar_recepcion.html', {
        'orden': orden,
        'items_solicitud': items_solicitud
    })

# ST-7.5 Consultar historial de auditoría
@login_required
def historial_auditoria(request):
    if not request.user.groups.filter(name="Administrador").exists():
        return HttpResponseForbidden("No tienes permisos para ver la auditoría.")

    registros = Auditoria.objects.all().order_by('-fecha_hora')
    return render(request, 'historial_auditoria.html', {'registros': registros})
