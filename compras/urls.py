# ============================================================
# Sprint 2 - HU-01: Registrar Solicitud de Compra
# Integrante encargado: ______
# ============================================================
from django.urls import path

from . import views

urlpatterns = [
    path("registrar/", views.registrar_solicitud_view, name="compras_registrar_solicitud"),
    path("", views.listado_solicitudes_view, name="compras_listado_solicitudes"),
    path("editar/<int:pk>/", views.editar_solicitud_view, name="compras_editar_solicitud"),
    path("verificar/<int:pk>/", views.verificar_stock_view, name="compras_verificar_stock"),
    path("pendientes/", views.bandeja_pendientes_view, name="compras_bandeja_pendientes"),
    path("aprobar/<int:pk>/", views.aprobar_solicitud_view, name="compras_aprobar_solicitud"),
    path("rechazar/<int:pk>/", views.rechazar_solicitud_view, name="compras_rechazar_solicitud"),
    path("proveedores/nuevo/", views.registrar_proveedor_view, name="compras_registrar_proveedor"),
    path("proveedores/", views.listado_proveedores_view, name="compras_listado_proveedores"),
    path("cotizacion/crear/<int:pk>/", views.crear_solicitud_cotizacion_view, name="compras_crear_solicitud_cotizacion"),
    path("cotizacion/<int:pk>/", views.ver_cotizaciones_view, name="compras_ver_cotizaciones"),
    path("cotizacion/seleccionar/<int:pk>/", views.seleccionar_ganadora_view, name="compras_seleccionar_ganadora"),
    path("orden/<int:pk>/", views.ver_orden_view, name="compras_ver_orden"),
    path("ordenes/", views.listado_ordenes_view, name="compras_listado_ordenes"),
    path("cotizacion/<int:pk>/agregar-proveedor/", views.agregar_proveedor_cotizacion_view, name="compras_agregar_proveedor_cotizacion"),
    path("orden/<int:pk>/imprimir/", views.imprimir_orden_view, name="compras_imprimir_orden"),
    path("orden/<int:pk>/pdf/", views.exportar_orden_pdf_view, name="compras_exportar_orden_pdf"),
    path("recepcion/pendientes/", views.ordenes_pendientes_recepcion_view, name="compras_ordenes_pendientes_recepcion"),
    path("recepcion/registrar/<int:pk>/", views.registrar_recepcion_view, name="compras_registrar_recepcion"),
    path("recepcion/<int:pk>/", views.ver_recepcion_view, name="compras_ver_recepcion"),
    path("inventario/verificar/<str:codigo_producto>/", views.verificar_inventario_actualizado_view, name="compras_verificar_inventario"),
    path("inventario/", views.buscar_inventario_view, name="compras_buscar_inventario"),
    path("auditoria/", views.historial_auditoria_view, name="compras_historial_auditoria"),
]