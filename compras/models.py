# ============================================================
# Sprint 2 - HU-01: Registrar Solicitud de Compra
# Integrante encargado: ______   <- pon aquí tu nombre para el commit
# ============================================================
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class SolicitudCompra(models.Model):
    ESTADO_PENDIENTE = "PENDIENTE"
    ESTADO_HAY_STOCK = "HAY_STOCK"
    ESTADO_SIN_STOCK = "SIN_STOCK"
    ESTADO_APROBADA = "APROBADA"
    ESTADO_RECHAZADA = "RECHAZADA"
    ESTADO_COMPLETADA = "COMPLETADA"
    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE, "Pendiente"),
        (ESTADO_HAY_STOCK, "Hay stock (atendida desde inventario)"),
        (ESTADO_SIN_STOCK, "Sin stock (pasa a cotización)"),
        (ESTADO_APROBADA, "Aprobada"),
        (ESTADO_RECHAZADA, "Rechazada"),
        (ESTADO_COMPLETADA, "Completada"),
    ]

    # ST-2.2: identificador único generado automáticamente
    codigo_solicitud = models.CharField(max_length=20, unique=True, editable=False)

    # TODO: cuando se junte con el proyecto de logística, cambiar
    # producto_codigo (CharField) por:
    #   producto = models.ForeignKey("inventory.Producto", on_delete=models.PROTECT)
    producto_codigo = models.CharField(max_length=50)
    producto_nombre = models.CharField(max_length=200)

    cantidad_solicitada = models.PositiveIntegerField()
    justificacion = models.TextField(blank=True)

    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_PENDIENTE)

    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="solicitudes_compra"
    )

    # ST-2.4: fecha y hora de registro
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def clean(self):
        # ST-2.3: cantidades mayores a cero
        if self.cantidad_solicitada is not None and self.cantidad_solicitada <= 0:
            raise ValidationError({"cantidad_solicitada": "La cantidad debe ser mayor a cero."})

    def save(self, *args, **kwargs):
        if not self.codigo_solicitud:
            self.codigo_solicitud = self._generar_codigo()
        self.full_clean()
        super().save(*args, **kwargs)

    def _generar_codigo(self):
        # ST-2.2: código único simple tipo SC-0001, SC-0002, ...
        ultimo = SolicitudCompra.objects.order_by("-id").first()
        siguiente = (ultimo.id + 1) if ultimo else 1
        return f"SC-{siguiente:04d}"

    def __str__(self):
        return f"{self.codigo_solicitud} - {self.producto_nombre}"
# ============================================================
# Sprint 4 - HU-04: Registrar Solicitudes de Cotización
# Sprint 4 - HU-05: Registrar Cotización de Proveedor
# Integrante encargado: ______
# ============================================================

class Proveedor(models.Model):
    # ST-4.1: registro y mantenimiento de proveedores
    nombre = models.CharField(max_length=200)
    ruc = models.CharField(max_length=20, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    correo = models.EmailField(blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class SolicitudCotizacion(models.Model):
    # ST-4.2: vinculada a una compra ya aprobada (o en curso de cotización)
    solicitud_compra = models.OneToOneField(
        SolicitudCompra, on_delete=models.CASCADE, related_name="solicitud_cotizacion"
    )
    # ST-4.3: uno o varios proveedores asociados
    proveedores = models.ManyToManyField(Proveedor, related_name="solicitudes_cotizacion")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cotización para {self.solicitud_compra.codigo_solicitud}"


class Cotizacion(models.Model):
    ESTADO_PENDIENTE = "PENDIENTE"
    ESTADO_ACEPTADA = "ACEPTADA"
    ESTADO_RECHAZADA = "RECHAZADA"
    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE, "Pendiente"),
        (ESTADO_ACEPTADA, "Aceptada"),
        (ESTADO_RECHAZADA, "Rechazada"),
    ]

    solicitud_cotizacion = models.ForeignKey(
        SolicitudCotizacion, on_delete=models.CASCADE, related_name="cotizaciones"
    )
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name="cotizaciones")

    # ST-4.4
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    # ST-4.5: ambos datos son obligatorios (por eso no llevan null/blank=True)
    tiempo_entrega_dias = models.PositiveIntegerField()
    vigencia = models.DateField()

    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_PENDIENTE)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.proveedor.nombre} - ${self.precio_unitario}"  

# ============================================================
# Sprint 5 - HU-06: Evaluar Cotizaciones
# Sprint 5 - HU-07: Generar Orden de Compra
# Integrante encargado: ______
# ============================================================

class OrdenCompra(models.Model):
    ESTADO_PENDIENTE = "PENDIENTE"
    ESTADO_RECIBIDA = "RECIBIDA"
    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE, "Pendiente"),
        (ESTADO_RECIBIDA, "Recibida"),
    ]
    numero_orden = models.CharField(max_length=20, unique=True, editable=False)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_PENDIENTE)
    cotizacion_ganadora = models.OneToOneField(
        Cotizacion, on_delete=models.PROTECT, related_name="orden_compra"
    )
    # ST-5.5: costo total = cantidad solicitada x precio unitario de la cotización ganadora
    costo_total = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_generada = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.numero_orden:
            self.numero_orden = self._generar_numero()
        super().save(*args, **kwargs)

    def _generar_numero(self):
        ultimo = OrdenCompra.objects.order_by("-id").first()
        siguiente = (ultimo.id + 1) if ultimo else 1
        return f"OC-{siguiente:04d}"

    def __str__(self):
        return self.numero_orden
    
# ============================================================
# Sprint 6 - HU-09: Seleccionar Orden Pendiente de Recepción
# Sprint 6 - HU-10: Registrar Recepción de Productos
# Integrante encargado: ______
# ============================================================

class Recepcion(models.Model):
    orden_compra = models.OneToOneField(
        OrdenCompra, on_delete=models.CASCADE, related_name="recepcion"
    )
    # ST-6.4: cantidades realmente recibidas
    cantidad_recibida = models.PositiveIntegerField()
    observaciones = models.TextField(blank=True)
    # ST-6.5: se calcula solo, comparando contra lo solicitado en la orden
    tiene_diferencia = models.BooleanField(default=False)
    fecha_recepcion = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        cantidad_esperada = self.orden_compra.cotizacion_ganadora.solicitud_cotizacion.solicitud_compra.cantidad_solicitada
        self.tiene_diferencia = self.cantidad_recibida != cantidad_esperada
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Recepción de {self.orden_compra.numero_orden}"

# ============================================================
# Sprint 7 - HU-14: Auditoría de Operaciones
# Integrante encargado: ______
# ============================================================

class AuditoriaAccion(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="acciones_auditoria"
    )
    accion = models.CharField(max_length=100)
    detalle = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.fecha:%Y-%m-%d %H:%M} - {self.accion}"        