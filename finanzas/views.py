from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from .forms import IngresoForm, GastoForm, VencimientoForm
from .models import Deuda, Ingreso, Gasto, Vencimiento


def _totales_mes(model, field_name):
    """Agrega el total del mes actual para el campo indicado."""
    today = date.today()
    return (
        model.objects.filter(fecha__year=today.year, fecha__month=today.month)
        .aggregate(total=Sum(field_name))
        .get('total') or 0
    )


@login_required
def dashboard(request):
    """Dashboard resumido con totales y vencimientos próximos."""
    today = date.today()
    treinta_dias = today + timedelta(days=30)

    deuda_total = (
        Deuda.objects.filter(estado__in=['al_dia', 'en_curso'])
        .aggregate(total=Sum('monto_total'))
        .get('total')
        or 0
    )
    cuota_fija_total = (
        Deuda.objects.aggregate(total=Sum('cuota_mensual_aprox')).get('total') or 0
    )
    ingresos_mes = _totales_mes(Ingreso, 'monto')
    gastos_mes = _totales_mes(Gasto, 'monto')

    vencimientos_proximos = (
        Vencimiento.objects.filter(
            estado='pendiente',
            fecha__gte=today,
            fecha__lte=treinta_dias,
        )
        .order_by('fecha')[:10]
    )

    relacion_cuotas_ingresos = 0
    if ingresos_mes > 0:
        relacion_cuotas_ingresos = (cuota_fija_total / ingresos_mes) * 100

    contexto = {
        'deuda_total': deuda_total,
        'cuota_fija_total': cuota_fija_total,
        'ingresos_mes': ingresos_mes,
        'gastos_mes': gastos_mes,
        'saldo_mes': ingresos_mes - gastos_mes,
        'vencimientos_proximos': vencimientos_proximos,
        'relacion_cuotas_ingresos': relacion_cuotas_ingresos,
    }
    return render(request, 'finanzas/dashboard.html', contexto)


class ListaIngresosView(LoginRequiredMixin, ListView):
    model = Ingreso
    template_name = 'finanzas/ingresos_list.html'
    context_object_name = 'ingresos'
    ordering = ['-fecha', '-id']

    def post(self, request, *args, **kwargs):
        marcados = request.POST.getlist('confirmado')
        Ingreso.objects.update(confirmado=False)
        if marcados:
            Ingreso.objects.filter(pk__in=marcados).update(confirmado=True)
        messages.success(request, 'Ingresos actualizados.')
        return redirect('finanzas:lista_ingresos')


class CrearIngresoView(LoginRequiredMixin, CreateView):
    model = Ingreso
    form_class = IngresoForm
    template_name = 'finanzas/ingreso_form.html'
    success_url = reverse_lazy('finanzas:lista_ingresos')

    def form_valid(self, form):
        messages.success(self.request, 'Ingreso cargado correctamente.')
        return super().form_valid(form)


class ListaGastosView(LoginRequiredMixin, ListView):
    model = Gasto
    template_name = 'finanzas/gastos_list.html'
    context_object_name = 'gastos'
    ordering = ['-fecha', '-id']

    def post(self, request, *args, **kwargs):
        marcados = request.POST.getlist('pagado')
        Gasto.objects.update(pagado=False)
        if marcados:
            Gasto.objects.filter(pk__in=marcados).update(pagado=True)
        messages.success(request, 'Gastos actualizados.')
        return redirect('finanzas:lista_gastos')


class CrearGastoView(LoginRequiredMixin, CreateView):
    model = Gasto
    form_class = GastoForm
    template_name = 'finanzas/gasto_form.html'
    success_url = reverse_lazy('finanzas:lista_gastos')

    def form_valid(self, form):
        messages.success(self.request, 'Gasto cargado correctamente.')
        return super().form_valid(form)


class ListaVencimientosView(LoginRequiredMixin, ListView):
    model = Vencimiento
    template_name = 'finanzas/vencimientos.html'
    context_object_name = 'vencimientos'
    ordering = ['fecha', 'concepto']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hoy'] = date.today()
        return context


class CrearVencimientoView(LoginRequiredMixin, CreateView):
    model = Vencimiento
    form_class = VencimientoForm
    template_name = 'finanzas/vencimiento_form.html'
    success_url = reverse_lazy('finanzas:vencimientos')

    def form_valid(self, form):
        messages.success(self.request, 'Vencimiento cargado correctamente.')
        return super().form_valid(form)


class ListaDeudasView(LoginRequiredMixin, ListView):
    model = Deuda
    template_name = 'finanzas/deudas_list.html'
    context_object_name = 'deudas'
    ordering = ['prioridad', 'entidad__nombre']
