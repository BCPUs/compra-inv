from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

# ST-2.2 Implementar generación automática del identificador
# ST-2.4 Implementar registro de la solicitud

class SolicitudCompra(models.Model):
    ESTADOS = [
        ('Pendiente', 'Pendiente'),
        ('En Revision', 'En Revision'),
        ('Aprobada', 'Aprobada'),
        ('Rechazada', 'Rechazada'),
        ('Cotizada', 'Cotizada'),
        ('Orden Generada', 'Orden Generada'),
        ('Recibida', 'Recibida'),
        ('Completada', 'Completada'),
    ]

    codigo = models.CharField(max_length=20, unique=True, editable=False)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Pendiente')
    justificacion_rechazo = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.codigo:
            # Simple automatic code generation
            last_solicitud = SolicitudCompra.objects.all().order_by('id').last()
            if not last_solicitud:
                self.codigo = 'SC-0001'
            else:
                last_id = last_solicitud.id
                self.codigo = f'SC-{str(last_id + 1).zfill(4)}'
        super(SolicitudCompra, self).save(*args, **kwargs)

    def __str__(self):
        return self.codigo

class ItemSolicitud(models.Model):
    solicitud = models.ForeignKey(SolicitudCompra, related_name='items', on_delete=models.CASCADE)
    producto = models.CharField(max_length=100)
    cantidad = models.PositiveIntegerField()
    unidad_medida = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.producto} - {self.cantidad} {self.unidad_medida}"

# ST-4.1 Registrar proveedores
class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    ruc = models.CharField(max_length=20, unique=True)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return self.nombre

# ST-4.2 Registrar solicitud de cotización
# ST-4.3 Asociar proveedores a la solicitud
class SolicitudCotizacion(models.Model):
    solicitud_compra = models.OneToOneField(SolicitudCompra, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    proveedores = models.ManyToManyField(Proveedor)

    def __str__(self):
        return f"Cotización para {self.solicitud_compra.codigo}"

# ST-4.4 Registrar precio unitario
# ST-4.5 Registrar tiempo de entrega y vigencia
class Cotizacion(models.Model):
    solicitud_cotizacion = models.ForeignKey(SolicitudCotizacion, related_name='cotizaciones', on_delete=models.CASCADE)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2) # Simple version, usually per item
    tiempo_entrega_dias = models.PositiveIntegerField()
    vigencia_dias = models.PositiveIntegerField()
    fecha_registro = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=[('Pendiente', 'Pendiente'), ('Aceptada', 'Aceptada'), ('Rechazada', 'Rechazada')], default='Pendiente')

    def __str__(self):
        return f"Cotización de {self.proveedor.nombre} para {self.solicitud_cotizacion.solicitud_compra.codigo}"

# ST-5.4 Generar orden de compra
# ST-5.5 Calcular costo total
class OrdenCompra(models.Model):
    cotizacion = models.OneToOneField(Cotizacion, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=20, unique=True, editable=False)
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    costo_total = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    estado = models.CharField(max_length=20, choices=[('Pendiente', 'Pendiente'), ('Recibida', 'Recibida')], default='Pendiente')

    def save(self, *args, **kwargs):
        if not self.codigo:
            last_oc = OrdenCompra.objects.all().order_by('id').last()
            if not last_oc:
                self.codigo = 'OC-0001'
            else:
                last_oc_id = last_oc.id
                self.codigo = f'OC-{str(last_oc_id + 1).zfill(4)}'

        # Calculate total cost based on quantity from purchase request
        items = self.cotizacion.solicitud_cotizacion.solicitud_compra.items.all()
        total = 0
        for item in items:
            total += item.cantidad * self.cotizacion.precio_unitario
        self.costo_total = total

        super(OrdenCompra, self).save(*args, **kwargs)

    def __str__(self):
        return self.codigo

# ST-6.4 Registrar recepción de productos
# ST-6.5 Validar recepción contra la orden
class RecepcionMercancia(models.Model):
    orden_compra = models.OneToOneField(OrdenCompra, on_delete=models.CASCADE)
    fecha_recepcion = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Recepción OC: {self.orden_compra.codigo}"

class ItemRecepcion(models.Model):
    recepcion = models.ForeignKey(RecepcionMercancia, related_name='items', on_delete=models.CASCADE)
    item_solicitud = models.ForeignKey(ItemSolicitud, on_delete=models.CASCADE)
    cantidad_recibida = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.item_solicitud.producto}: {self.cantidad_recibida} recibidos"

# ST-7.4 Registrar acciones de auditoría
class Auditoria(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    accion = models.CharField(max_length=100)
    detalle = models.TextField()
    fecha_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.accion} - {self.fecha_hora}"
