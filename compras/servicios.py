# ============================================================
# Sprint 3 - HU-02: Verificar Disponibilidad de Inventario
# Integrante encargado: ______
# ============================================================
"""
Puente hacia el módulo de Logística/Inventario.

Por ahora esta función SIMULA la consulta porque compras y logística
están en proyectos Django separados. Cuando se junten en un solo
proyecto, esta es la ÚNICA función que hay que cambiar: en vez de
devolver datos de prueba, debe consultar directamente:

    from inventory.models import Producto
    producto = Producto.objects.get(codigo=codigo_producto)
    return {"existe": True, "stock_disponible": producto.stock_total}

Así el resto de la app (vistas, formularios) no cambia nada.
"""

# Datos de prueba simulando el inventario real de logística
_INVENTARIO_SIMULADO = {
    "123456": {"nombre": "Atun", "stock_disponible": 50},
    "789012": {"nombre": "Arroz", "stock_disponible": 0},
}


def consultar_disponibilidad(codigo_producto):
    """
    ST-3.1 / ST-3.2: consulta si el producto existe y cuánto stock tiene.
    Devuelve un dict: {"existe": bool, "stock_disponible": int, "nombre": str}
    """
    producto = _INVENTARIO_SIMULADO.get(codigo_producto)
    if producto is None:
        return {"existe": False, "stock_disponible": 0, "nombre": None}
    return {"existe": True, "stock_disponible": producto["stock_disponible"], "nombre": producto["nombre"]}


def hay_stock_suficiente(codigo_producto, cantidad_solicitada):
    """ST-3.2: compara la cantidad solicitada con el stock disponible."""
    info = consultar_disponibilidad(codigo_producto)
    return info["existe"] and info["stock_disponible"] >= cantidad_solicitada

def actualizar_inventario(codigo_producto, cantidad):
    """
    ST-7.1: actualiza el inventario después de recibir la compra.

    Por ahora SIMULA la actualización. Cuando se junten los proyectos,
    reemplazar por la llamada real:

        from inventory.services import InventoryService
        from inventory.models import Producto
        producto = Producto.objects.get(codigo=codigo_producto)
        InventoryService.registrar_movimiento(
            producto, cantidad, tipo="ENTRADA", usuario=..., motivo="Recepción de compra"
        )

    Devuelve True si la actualización fue exitosa (simulado siempre True).
    """
    if codigo_producto in _INVENTARIO_SIMULADO:
        _INVENTARIO_SIMULADO[codigo_producto]["stock_disponible"] += cantidad
    return True

# ============================================================
# Sprint 7 - HU-14: Auditoría de Operaciones
# Integrante encargado: ______
# ============================================================

def registrar_auditoria(usuario, accion, detalle=""):
    """ST-7.4: registra una acción realizada durante el proceso de compra."""
    from .models import AuditoriaAccion
    AuditoriaAccion.objects.create(usuario=usuario, accion=accion, detalle=detalle)