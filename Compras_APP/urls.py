from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/usuarios/",views.usuarios, name="usuarios"),

    # Sprint 2
    path("solicitudes/", views.listar_solicitudes, name="listar_solicitudes"),
    path("solicitudes/registrar/", views.registrar_solicitud, name="registrar_solicitud"),
    path("solicitudes/editar/<int:pk>/", views.editar_solicitud, name="editar_solicitud"),

    # Sprint 3
    path("bandeja/", views.bandeja_pendientes, name="bandeja_pendientes"),
    path("solicitudes/aprobar/<int:pk>/", views.aprobar_solicitud, name="aprobar_solicitud"),
    path("solicitudes/rechazar/<int:pk>/", views.rechazar_solicitud, name="rechazar_solicitud"),

    # Sprint 4
    path("proveedores/", views.listar_proveedores, name="listar_proveedores"),
    path("proveedores/registrar/", views.registrar_proveedor, name="registrar_proveedor"),
    path("solicitudes/cotizar/<int:solicitud_pk>/", views.registrar_solicitud_cotizacion, name="registrar_solicitud_cotizacion"),
    path("cotizaciones/<int:sol_cot_pk>/", views.consultar_cotizaciones, name="consultar_cotizaciones"),
    path("cotizaciones/<int:sol_cot_pk>/registrar/", views.registrar_cotizacion, name="registrar_cotizacion"),

    # Sprint 5
    path("cotizaciones/<int:sol_cot_pk>/comparar/", views.comparar_cotizaciones, name="comparar_cotizaciones"),
    path("cotizaciones/seleccionar/<int:cotizacion_pk>/", views.seleccionar_ganador, name="seleccionar_ganador"),
    path("ordenes/", views.listar_ordenes, name="listar_ordenes"),

    # Sprint 6
    path("ordenes/imprimir/<int:pk>/", views.imprimir_orden, name="imprimir_orden"),
    path("ordenes/pdf/<int:pk>/", views.exportar_pdf_orden, name="exportar_pdf_orden"),
    path("recepcion/pendientes/", views.listar_ordenes_pendientes, name="listar_ordenes_pendientes"),
    path("recepcion/registrar/<int:pk>/", views.registrar_recepcion, name="registrar_recepcion"),

    # Sprint 7
    path("auditoria/", views.historial_auditoria, name="historial_auditoria"),
]
