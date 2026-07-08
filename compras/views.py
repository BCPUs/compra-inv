# ============================================================
# Sprint 2 - HU-01: Registrar Solicitud de Compra
# Sprint 3 - HU-02: Verificar Disponibilidad de Inventario
# Integrante encargado: ______   <- pon aquí tu nombre para el commit
# ============================================================
from django.shortcuts import get_object_or_404, redirect, render

from .forms import SolicitudCompraForm
from .models import SolicitudCompra
from .servicios import hay_stock_suficiente
from .forms import CotizacionForm, ProveedorForm, SolicitudCotizacionForm
from .models import Cotizacion, Proveedor, SolicitudCotizacion
from .models import Cotizacion, OrdenCompra, Proveedor, SolicitudCotizacion
from io import BytesIO
from .models import Cotizacion, OrdenCompra, Proveedor, Recepcion, SolicitudCotizacion
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from .servicios import actualizar_inventario, hay_stock_suficiente
from .servicios import actualizar_inventario, hay_stock_suficiente, registrar_auditoria
from .models import AuditoriaAccion, Cotizacion, OrdenCompra, Proveedor, Recepcion, SolicitudCotizacion

def registrar_solicitud_view(request):
    if request.method == "POST":
        form = SolicitudCompraForm(request.POST)
        if form.is_valid():
            solicitud = form.save()
            registrar_auditoria(request.user if request.user.is_authenticated else None,
                                 "Registrar solicitud", f"{solicitud.codigo_solicitud}")
            return redirect("compras_listado_solicitudes")
    else:
        form = SolicitudCompraForm()

    return render(request, "compras/registrar_solicitud.html", {"form": form})


def listado_solicitudes_view(request):
    solicitudes = SolicitudCompra.objects.all().order_by("-fecha_registro")
    return render(request, "compras/listado_solicitudes.html", {"solicitudes": solicitudes})


def editar_solicitud_view(request, pk):
    solicitud = get_object_or_404(SolicitudCompra, pk=pk)

    # ST-2.6: se bloquea la edición si ya fue aprobada, rechazada o completada
    if solicitud.estado in (
        SolicitudCompra.ESTADO_APROBADA,
        SolicitudCompra.ESTADO_RECHAZADA,
        SolicitudCompra.ESTADO_COMPLETADA,
    ):
        return render(request, "compras/editar_no_permitido.html", {"solicitud": solicitud})

    if request.method == "POST":
        form = SolicitudCompraForm(request.POST, instance=solicitud)
        if form.is_valid():
            form.save()
            return redirect("compras_listado_solicitudes")
    else:
        form = SolicitudCompraForm(instance=solicitud)

    return render(request, "compras/editar_solicitud.html", {"form": form, "solicitud": solicitud})


def verificar_stock_view(request, pk):
    solicitud = get_object_or_404(SolicitudCompra, pk=pk)

    if hay_stock_suficiente(solicitud.producto_codigo, solicitud.cantidad_solicitada):
        solicitud.estado = SolicitudCompra.ESTADO_HAY_STOCK
    else:
        solicitud.estado = SolicitudCompra.ESTADO_SIN_STOCK
    solicitud.save()

    return redirect("compras_listado_solicitudes")

def bandeja_pendientes_view(request):
    # ST-3.4: solo se muestran solicitudes que requieren revisión
    # (ya se verificó el stock, y todavía no hay decisión de aprobación)
    solicitudes = SolicitudCompra.objects.filter(
        estado__in=[SolicitudCompra.ESTADO_HAY_STOCK, SolicitudCompra.ESTADO_SIN_STOCK]
    ).order_by("fecha_registro")
    return render(request, "compras/bandeja_pendientes.html", {"solicitudes": solicitudes})

def aprobar_solicitud_view(request, pk):
    solicitud = get_object_or_404(SolicitudCompra, pk=pk)
    solicitud.estado = SolicitudCompra.ESTADO_APROBADA
    solicitud.save()
    registrar_auditoria(request.user if request.user.is_authenticated else None,
                         "Aprobar solicitud", f"{solicitud.codigo_solicitud}")
    return redirect("compras_bandeja_pendientes")


def rechazar_solicitud_view(request, pk):
    solicitud = get_object_or_404(SolicitudCompra, pk=pk)

    if request.method == "POST":
        justificacion = request.POST.get("justificacion", "").strip()
        # ST-3.6: no se puede rechazar sin justificación
        if not justificacion:
            return render(request, "compras/rechazar_solicitud.html", {
                "solicitud": solicitud,
                "error": "Debes ingresar una justificación para rechazar.",
            })
        solicitud.estado = SolicitudCompra.ESTADO_RECHAZADA
        solicitud.justificacion = justificacion
        solicitud.save()
        registrar_auditoria(request.user if request.user.is_authenticated else None,
                             "Rechazar solicitud", f"{solicitud.codigo_solicitud} - {justificacion}")
        return redirect("compras_bandeja_pendientes")

    return render(request, "compras/rechazar_solicitud.html", {"solicitud": solicitud})

# ============================================================
# Sprint 4 - HU-04/HU-05
# Integrante encargado: ______
# ============================================================

def registrar_proveedor_view(request):
    # ST-4.1
    if request.method == "POST":
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("compras_listado_proveedores")
    else:
        form = ProveedorForm()
    return render(request, "compras/registrar_proveedor.html", {"form": form})


def listado_proveedores_view(request):
    proveedores = Proveedor.objects.filter(activo=True).order_by("nombre")
    return render(request, "compras/listado_proveedores.html", {"proveedores": proveedores})


def crear_solicitud_cotizacion_view(request, pk):
    solicitud_compra = get_object_or_404(SolicitudCompra, pk=pk)

    # Si ya existe una solicitud de cotización para esta compra, no crear otra:
    # la mostramos directamente (ahí se pueden seguir agregando cotizaciones)
    solicitud_cotizacion_existente = getattr(solicitud_compra, "solicitud_cotizacion", None)
    if solicitud_cotizacion_existente is not None:
        return redirect("compras_ver_cotizaciones", pk=solicitud_cotizacion_existente.pk)

    if request.method == "POST":
        form = SolicitudCotizacionForm(request.POST)
        if form.is_valid():
            solicitud_cotizacion = form.save(commit=False)
            solicitud_cotizacion.solicitud_compra = solicitud_compra
            solicitud_cotizacion.save()
            form.save_m2m()
            return redirect("compras_ver_cotizaciones", pk=solicitud_cotizacion.pk)
    else:
        form = SolicitudCotizacionForm()

    return render(request, "compras/crear_solicitud_cotizacion.html", {
        "form": form,
        "solicitud_compra": solicitud_compra,
    })

def ver_cotizaciones_view(request, pk):
    # ST-4.6: mostrar todas las cotizaciones asociadas a una solicitud
    solicitud_cotizacion = get_object_or_404(SolicitudCotizacion, pk=pk)
    cotizaciones = solicitud_cotizacion.cotizaciones.all()

    if request.method == "POST":
        # ST-4.4: registrar el precio ofrecido por cada proveedor
        cot_form = CotizacionForm(request.POST)
        if cot_form.is_valid():
            cotizacion = cot_form.save(commit=False)
            cotizacion.solicitud_cotizacion = solicitud_cotizacion
            cotizacion.save()
            return redirect("compras_ver_cotizaciones", pk=pk)
    else:
        cot_form = CotizacionForm()
        # solo mostramos los proveedores que se asociaron a esta solicitud
        cot_form.fields["proveedor"].queryset = solicitud_cotizacion.proveedores.all()

    return render(request, "compras/ver_cotizaciones.html", {
        "solicitud_cotizacion": solicitud_cotizacion,
        "cotizaciones": cotizaciones,
        "cot_form": cot_form,
    })
def agregar_proveedor_cotizacion_view(request, pk):
    solicitud_cotizacion = get_object_or_404(SolicitudCotizacion, pk=pk)

    if request.method == "POST":
        proveedor_id = request.POST.get("proveedor")
        if proveedor_id:
            proveedor = get_object_or_404(Proveedor, pk=proveedor_id)
            solicitud_cotizacion.proveedores.add(proveedor)
        return redirect("compras_ver_cotizaciones", pk=pk)

    # proveedores que todavía no están asociados a esta solicitud
    proveedores_disponibles = Proveedor.objects.filter(activo=True).exclude(
        pk__in=solicitud_cotizacion.proveedores.values_list("pk", flat=True)
    )
    return render(request, "compras/agregar_proveedor_cotizacion.html", {
        "solicitud_cotizacion": solicitud_cotizacion,
        "proveedores_disponibles": proveedores_disponibles,
    })

# ============================================================
# Sprint 5 - HU-06/HU-07
# Integrante encargado: ______
# ============================================================

def seleccionar_ganadora_view(request, pk):
    cotizacion = get_object_or_404(Cotizacion, pk=pk)
    solicitud_cotizacion = cotizacion.solicitud_cotizacion
    solicitud_compra = solicitud_cotizacion.solicitud_compra

    # ST-5.3: la seleccionada queda ACEPTADA, todas las demás de esa
    # solicitud quedan RECHAZADAS automáticamente
    solicitud_cotizacion.cotizaciones.exclude(pk=cotizacion.pk).update(
        estado=Cotizacion.ESTADO_RECHAZADA
    )
    cotizacion.estado = Cotizacion.ESTADO_ACEPTADA
    cotizacion.save()

    # ST-5.4 y ST-5.5: genera la orden de compra y calcula el costo total
    costo_total = solicitud_compra.cantidad_solicitada * cotizacion.precio_unitario
    orden = OrdenCompra.objects.create(
        cotizacion_ganadora=cotizacion,
        costo_total=costo_total,
    )

    registrar_auditoria(request.user if request.user.is_authenticated else None,
                         "Generar orden de compra", f"{orden.numero_orden}")

    return redirect("compras_ver_orden", pk=orden.pk)


def ver_orden_view(request, pk):
    orden = get_object_or_404(OrdenCompra, pk=pk)
    return render(request, "compras/ver_orden.html", {"orden": orden})


def listado_ordenes_view(request):
    # ST-5.6
    ordenes = OrdenCompra.objects.all().order_by("-fecha_generada")
    return render(request, "compras/listado_ordenes.html", {"ordenes": ordenes})

# ============================================================
# Sprint 6 - HU-08: Imprimir Orden de Compra
# Integrante encargado: ______
# ============================================================

def imprimir_orden_view(request, pk):
    orden = get_object_or_404(OrdenCompra, pk=pk)
    return render(request, "compras/imprimir_orden.html", {"orden": orden})
def exportar_orden_pdf_view(request, pk):
    orden = get_object_or_404(OrdenCompra, pk=pk)
    html = render_to_string("compras/imprimir_orden.html", {"orden": orden})

    buffer = BytesIO()
    pisa.CreatePDF(html, dest=buffer)

    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{orden.numero_orden}.pdf"'
    return response
def ordenes_pendientes_recepcion_view(request):
    # ST-6.3: solo se muestran órdenes pendientes
    ordenes = OrdenCompra.objects.filter(estado=OrdenCompra.ESTADO_PENDIENTE).order_by("fecha_generada")
    return render(request, "compras/ordenes_pendientes_recepcion.html", {"ordenes": ordenes})
def registrar_recepcion_view(request, pk):
    orden = get_object_or_404(OrdenCompra, pk=pk)
    cantidad_esperada = orden.cotizacion_ganadora.solicitud_cotizacion.solicitud_compra.cantidad_solicitada

    if request.method == "POST":
        cantidad_recibida = int(request.POST.get("cantidad_recibida", 0))
        observaciones = request.POST.get("observaciones", "")

        recepcion = Recepcion.objects.create(
            orden_compra=orden,
            cantidad_recibida=cantidad_recibida,
            observaciones=observaciones,
        )

        # ST-6.6: la orden queda marcada como recibida
        orden.estado = OrdenCompra.ESTADO_RECIBIDA
        orden.save()

        # ST-7.1: actualizar inventario con lo recibido
        solicitud_compra = orden.cotizacion_ganadora.solicitud_cotizacion.solicitud_compra
        actualizar_inventario(solicitud_compra.producto_codigo, cantidad_recibida)

        # ST-7.2: la compra queda como completada
        solicitud_compra.estado = SolicitudCompra.ESTADO_COMPLETADA
        solicitud_compra.save()

        registrar_auditoria(request.user if request.user.is_authenticated else None,
                             "Registrar recepción", f"{orden.numero_orden} - cantidad: {cantidad_recibida}")

        return redirect("compras_ver_recepcion", pk=recepcion.pk)

    return render(request, "compras/registrar_recepcion.html", {
        "orden": orden,
        "cantidad_esperada": cantidad_esperada,
    })

def ver_recepcion_view(request, pk):
    recepcion = get_object_or_404(Recepcion, pk=pk)
    solicitud_compra = recepcion.orden_compra.cotizacion_ganadora.solicitud_cotizacion.solicitud_compra
    return render(request, "compras/ver_recepcion.html", {
        "recepcion": recepcion,
        "cantidad_esperada": solicitud_compra.cantidad_solicitada,
        "producto_codigo": solicitud_compra.producto_codigo,
    })

def registrar_recepcion_view(request, pk):
    orden = get_object_or_404(OrdenCompra, pk=pk)
    cantidad_esperada = orden.cotizacion_ganadora.solicitud_cotizacion.solicitud_compra.cantidad_solicitada

    if request.method == "POST":
        cantidad_recibida = int(request.POST.get("cantidad_recibida", 0))
        observaciones = request.POST.get("observaciones", "")

        recepcion = Recepcion.objects.create(
            orden_compra=orden,
            cantidad_recibida=cantidad_recibida,
            observaciones=observaciones,
        )

        # ST-6.6: la orden queda marcada como recibida
        orden.estado = OrdenCompra.ESTADO_RECIBIDA
        orden.save()
#sprint 7
        # ST-7.1: actualizar inventario con lo recibido
        solicitud_compra = orden.cotizacion_ganadora.solicitud_cotizacion.solicitud_compra
        actualizar_inventario(solicitud_compra.producto_codigo, cantidad_recibida)

        # ST-7.2: la compra queda como completada
        solicitud_compra.estado = SolicitudCompra.ESTADO_COMPLETADA
        solicitud_compra.save()

        return redirect("compras_ver_recepcion", pk=recepcion.pk)

    return render(request, "compras/registrar_recepcion.html", {
        "orden": orden,
        "cantidad_esperada": cantidad_esperada,
    })
def verificar_inventario_actualizado_view(request, codigo_producto):
    # ST-7.3: comprobar que las existencias se hayan actualizado correctamente
    from .servicios import consultar_disponibilidad
    info = consultar_disponibilidad(codigo_producto)
    return render(request, "compras/verificar_inventario.html", {"info": info, "codigo": codigo_producto})
def buscar_inventario_view(request):
    codigo = request.GET.get("codigo", "").strip()
    info = None
    if codigo:
        from .servicios import consultar_disponibilidad
        info = consultar_disponibilidad(codigo)
    return render(request, "compras/buscar_inventario.html", {"info": info, "codigo": codigo})
def historial_auditoria_view(request):
    # ST-7.5: consulta del historial de acciones
    acciones = AuditoriaAccion.objects.all().order_by("-fecha")
    return render(request, "compras/historial_auditoria.html", {"acciones": acciones})