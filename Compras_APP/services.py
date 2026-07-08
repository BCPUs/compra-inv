import requests

# ST-3.1 Integrar consulta a la API de Inventarios
# ST-7.1 Integrar actualización del inventario
# ST-7.3 Verificar actualización del inventario

def consultar_inventario(producto):
    """
    Consulta la disponibilidad de un producto en la API de Inventarios.
    En un entorno real, esto haría una petición HTTP.
    """
    # URL de ejemplo para la API de Inventarios (Logística)
    # API_URL = "http://logistica.api/inventario/"

    # Simulando respuesta de la API
    inventario_simulado = {
        'Laptop': 10,
        'Monitor': 5,
        'Teclado': 20,
        'Mouse': 50,
        'Silla': 2,
    }

    return inventario_simulado.get(producto, 0)

def actualizar_inventario(producto, cantidad):
    """
    Actualiza el stock en la API de Inventarios después de la recepción.
    """
    # API_URL = "http://logistica.api/inventario/update/"
    # payload = {'producto': producto, 'cantidad': cantidad}
    # response = requests.post(API_URL, json=payload)
    # return response.status_code == 200

    print(f"Sincronizando con Logística: {producto} +{cantidad}")
    return True

# ST-3.2 Validar disponibilidad de stock
# ST-3.3 Actualizar estado de la solicitud
def validar_disponibilidad_stock(solicitud):
    """
    Compara la cantidad solicitada con el stock disponible y actualiza el estado.
    """
    disponibilidad_total = True
    for item in solicitud.items.all():
        stock = consultar_inventario(item.producto)
        if item.cantidad > stock:
            disponibilidad_total = False
            break

    if disponibilidad_total:
        solicitud.estado = 'En Revision'
    else:
        solicitud.estado = 'Rechazada'
        solicitud.justificacion_rechazo = "Stock insuficiente en inventario."

    solicitud.save()
    return disponibilidad_total
