# ============================================================
# Sprint 2 - HU-01: Registrar Solicitud de Compra
# Integrante encargado: ______   <- pon aquí tu nombre para el commit
# ============================================================
from django import forms

from .models import SolicitudCompra


class SolicitudCompraForm(forms.ModelForm):
    class Meta:
        model = SolicitudCompra
        fields = [
            "producto_codigo",
            "producto_nombre",
            "cantidad_solicitada",
            "justificacion",
        ]
        widgets = {
            "justificacion": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_cantidad_solicitada(self):
        # ST-2.3: cantidad mayor a cero (refuerzo a nivel de formulario,
        # además de la validación que ya está en el modelo)
        cantidad = self.cleaned_data.get("cantidad_solicitada")
        if cantidad is not None and cantidad <= 0:
            raise forms.ValidationError("La cantidad debe ser mayor a cero.")
        return cantidad

    def clean_producto_codigo(self):
        codigo = self.cleaned_data.get("producto_codigo")
        if not codigo or not codigo.strip():
            raise forms.ValidationError("El código de producto es obligatorio.")
        return codigo.strip()
    

# ============================================================
# Sprint 4 - HU-04/HU-05
# Integrante encargado: ______
# ============================================================
from .models import Cotizacion, Proveedor, SolicitudCotizacion


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ["nombre", "ruc", "telefono", "correo"]


class SolicitudCotizacionForm(forms.ModelForm):
    class Meta:
        model = SolicitudCotizacion
        fields = ["proveedores"]
        widgets = {
            "proveedores": forms.CheckboxSelectMultiple(),  # ST-4.3: elegir uno o varios
        }


class CotizacionForm(forms.ModelForm):
    class Meta:
        model = Cotizacion
        fields = ["proveedor", "precio_unitario", "tiempo_entrega_dias", "vigencia"]
        widgets = {
            "vigencia": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        # ST-4.5: ambos datos son obligatorios (Django ya lo exige por el modelo,
        # esto es un refuerzo explícito por si alguien manda el form vacío a mano)
        if not cleaned_data.get("tiempo_entrega_dias"):
            self.add_error("tiempo_entrega_dias", "El tiempo de entrega es obligatorio.")
        if not cleaned_data.get("vigencia"):
            self.add_error("vigencia", "La vigencia es obligatoria.")
        return cleaned_data    