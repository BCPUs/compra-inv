from django import forms
from .models import SolicitudCompra, ItemSolicitud, Proveedor, Cotizacion
from django.forms import inlineformset_factory

# ST-2.1 Crear formulario de solicitud
# ST-2.3 Implementar validaciones del formulario

class SolicitudCompraForm(forms.ModelForm):
    class Meta:
        model = SolicitudCompra
        fields = [] # Codigo and Usuario are automatic

class ItemSolicitudForm(forms.ModelForm):
    class Meta:
        model = ItemSolicitud
        fields = ['producto', 'cantidad', 'unidad_medida']

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad is not None and cantidad <= 0:
            raise forms.ValidationError("La cantidad debe ser mayor a cero.")
        return cantidad

ItemSolicitudFormSet = inlineformset_factory(
    SolicitudCompra,
    ItemSolicitud,
    form=ItemSolicitudForm,
    extra=1,
    can_delete=True
)

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = '__all__'

class CotizacionForm(forms.ModelForm):
    class Meta:
        model = Cotizacion
        fields = ['proveedor', 'precio_unitario', 'tiempo_entrega_dias', 'vigencia_dias']
