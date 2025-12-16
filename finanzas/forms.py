from datetime import date, timedelta

from django import forms

from .models import Ingreso, Gasto

PAST_LIMIT_YEARS = 50
FUTURE_LIMIT_YEARS = 5


class DateInput(forms.DateInput):
    input_type = 'date'

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('format', '%Y-%m-%d')
        super().__init__(*args, **kwargs)


def _validate_fecha(value):
    today = date.today()
    min_date = today - timedelta(days=365 * PAST_LIMIT_YEARS)
    max_date = today + timedelta(days=365 * FUTURE_LIMIT_YEARS)
    if not (min_date <= value <= max_date):
        raise forms.ValidationError('Fecha fuera de rango razonable.')


def _validate_monto(value):
    if value <= 0:
        raise forms.ValidationError('El monto debe ser mayor a 0.')


class IngresoForm(forms.ModelForm):
    class Meta:
        model = Ingreso
        fields = ['fecha', 'tipo', 'descripcion', 'monto', 'confirmado']
        widgets = {
            'fecha': DateInput(),
            'monto': forms.NumberInput(attrs={'step': '0.01'}),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['deuda_relacionada'].queryset = (
            self.fields['deuda_relacionada']
            .queryset
            .filter(tipo_deuda__in=['tarjeta', 'prestamo', 'otro'])
            .order_by('entidad__nombre', 'tipo_deuda')
        )
    def clean_fecha(self):
        value = self.cleaned_data['fecha']
        _validate_fecha(value)
        return value

    def clean_monto(self):
        value = self.cleaned_data['monto']
        _validate_monto(value)
        return value


class GastoForm(forms.ModelForm):
    class Meta:
        model = Gasto
        fields = [
            'fecha',
            'tipo',
            'categoria',
            'descripcion',
            'monto',
            'pagado',
            'deuda_relacionada',
        ]
        widgets = {
            'fecha': DateInput(),
            'monto': forms.NumberInput(attrs={'step': '0.01'}),
        }
        help_texts = {
            'deuda_relacionada': 'Si es un pago de deuda, vincúlalo aquí.',
        }

    def clean_fecha(self):
        value = self.cleaned_data['fecha']
        _validate_fecha(value)
        return value

    def clean_monto(self):
        value = self.cleaned_data['monto']
        _validate_monto(value)
        return value
