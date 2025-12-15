from datetime import date, timedelta

from django.db.models import Sum
from django.shortcuts import render

from .models import Deuda, Ingreso, Gasto, Vencimiento


def dashboard(request):
    hoy = date.today()
    treinta_dias = hoy + timedelta(days=30)

    deuda_total = Deuda.objects.filter(
        estado__in=['al_dia', 'en_curso']
    ).aggregate(total=Sum('monto_total'))['total'] or 0

    cuota_fija_total = Deuda.objects.aggregate(
        total=Sum('cuota_mensual_aprox')
    )['total'] or 0

    ingresos_mes = Ingreso.objects.filter(
        fecha__year=hoy.year,
        fecha__month=hoy.month,
    ).aggregate(total=Sum('monto'))['total'] or 0

    gastos_mes = Gasto.objects.filter(
        fecha__year=hoy.year,
        fecha__month=hoy.month,
    ).aggregate(total=Sum('monto'))['total'] or 0

    vencimientos_proximos = Vencimiento.objects.filter(
        estado='pendiente',
        fecha__gte=hoy,
        fecha__lte=treinta_dias,
    ).order_by('fecha')[:10]

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


def lista_deudas(request):
    deudas = Deuda.objects.order_by('prioridad', 'entidad__nombre')
    return render(request, 'finanzas/deudas_list.html', {'deudas': deudas})


def vencimientos(request):
    hoy = date.today()
    vencimientos_qs = Vencimiento.objects.order_by('fecha')
    return render(
        request,
        'finanzas/vencimientos.html',
        {'vencimientos': vencimientos_qs, 'hoy': hoy},
    )
