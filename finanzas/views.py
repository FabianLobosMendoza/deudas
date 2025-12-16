import calendar
from datetime import date, timedelta
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.management import call_command
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from django.views.generic.edit import UpdateView

from .forms import IngresoForm, GastoForm
from .models import Deuda, Ingreso, Gasto


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
    """
    Renderiza el dashboard principal.

    Params:
        request (HttpRequest): petición HTTP del usuario autenticado.

    Retorna:
        HttpResponse con los totales del mes, relación cuotas/ingresos y
        los gastos pendientes en los próximos 30 días.
    """
    today = date.today()
    month_param = request.GET.get('month')

    if month_param:
        try:
            anio_str, mes_str = month_param.split('-')
            anio_sel = int(anio_str)
            mes_sel = int(mes_str)
            selected_date = date(anio_sel, mes_sel, 1)
        except Exception:  # noqa: BLE001
            selected_date = date(today.year, today.month, 1)
    else:
        selected_date = date(today.year, today.month, 1)

    ultimo_dia = calendar.monthrange(selected_date.year, selected_date.month)[1]
    dias_labels = list(range(1, ultimo_dia + 1))

    ingresos_por_dia = []
    gastos_por_dia = []
    sobrante_por_dia = []
    saldo_acumulado = 0

    for dia in dias_labels:
        ingresos_dia = (
            Ingreso.objects.filter(
                fecha__year=selected_date.year,
                fecha__month=selected_date.month,
                fecha__day=dia,
                confirmado=True,
            )
            .aggregate(total=Sum('monto'))
            .get('total')
            or 0
        )
        gastos_dia = (
            Gasto.objects.filter(
                fecha__year=selected_date.year,
                fecha__month=selected_date.month,
                fecha__day=dia,
                pagado=True,
            )
            .aggregate(total=Sum('monto'))
            .get('total')
            or 0
        )
        ingresos_por_dia.append(float(ingresos_dia))
        gastos_por_dia.append(float(gastos_dia))
        saldo_acumulado += float(ingresos_dia) - float(gastos_dia)
        sobrante_por_dia.append(saldo_acumulado)

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
    saldo_mes = ingresos_mes - gastos_mes

    gastos_pendientes = (
        Gasto.objects.filter(
            pagado=False,
            fecha__gte=today,
            fecha__lte=treinta_dias,
        ).order_by('fecha')[:10]
    )

    relacion_cuotas_ingresos = 0
    if ingresos_mes > 0:
        relacion_cuotas_ingresos = (cuota_fija_total / ingresos_mes) * 100

    contexto = {
        'deuda_total': deuda_total,
        'cuota_fija_total': cuota_fija_total,
        'ingresos_mes': ingresos_mes,
        'gastos_mes': gastos_mes,
        'saldo_mes': saldo_mes,
        'gastos_pendientes': gastos_pendientes,
        'relacion_cuotas_ingresos': relacion_cuotas_ingresos,
        'dias_labels': dias_labels,
        'ingresos_por_dia': ingresos_por_dia,
        'gastos_por_dia': gastos_por_dia,
        'sobrante_por_dia': sobrante_por_dia,
        'month_str': f'{selected_date.year:04d}-{selected_date.month:02d}',
    }
    return render(request, 'finanzas/dashboard.html', contexto)


class ListaIngresosView(LoginRequiredMixin, ListView):
    """
    Lista de ingresos.

    Muestra ingresos filtrados según el switch "ver_todos" (solo no cobrados
    por defecto) y permite marcarlos como confirmados vía POST.
    """
    model = Ingreso
    template_name = 'finanzas/ingresos_list.html'
    context_object_name = 'ingresos'
    ordering = ['-fecha', '-id']

    def get_queryset(self):
        qs = super().get_queryset()
        ver_todos = self.request.GET.get('ver_todos') == '1'
        if not ver_todos:
            qs = qs.filter(confirmado=False)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ver_todos'] = self.request.GET.get('ver_todos') == '1'
        context['hoy'] = date.today()
        return context

    def post(self, request, *args, **kwargs):
        """
        Marca ingresos como confirmados según los checkboxes.

        Params:
            request (HttpRequest): incluye lista 'confirmado' con ids marcados.
        """
        marcados = request.POST.getlist('confirmado')
        Ingreso.objects.update(confirmado=False)
        if marcados:
            Ingreso.objects.filter(pk__in=marcados).update(confirmado=True)
        messages.success(request, 'Ingresos actualizados.')
        return redirect('finanzas:lista_ingresos')


class CrearIngresoView(LoginRequiredMixin, CreateView):
    """
    Alta de ingresos.

    Usa IngresoForm para validar y mostrar el formulario.
    """
    model = Ingreso
    form_class = IngresoForm
    template_name = 'finanzas/ingreso_form.html'
    success_url = reverse_lazy('finanzas:lista_ingresos')

    def form_valid(self, form):
        messages.success(self.request, 'Ingreso cargado correctamente.')
        return super().form_valid(form)


class EditarIngresoView(LoginRequiredMixin, UpdateView):
    """
    Edición de ingresos existentes.

    Params:
        pk (int): identificador del ingreso a editar.
    """
    model = Ingreso
    form_class = IngresoForm
    template_name = 'finanzas/ingreso_form.html'
    success_url = reverse_lazy('finanzas:lista_ingresos')
    extra_context = {'form_title': 'Editar ingreso'}

    def form_valid(self, form):
        messages.success(self.request, 'Ingreso actualizado correctamente.')
        return super().form_valid(form)


class ListaGastosView(LoginRequiredMixin, ListView):
    """
    Lista de gastos.

    Filtra por defecto gastos no pagados; el switch "ver_todos" muestra todos.
    Permite marcarlos como pagados vía POST.
    """
    model = Gasto
    template_name = 'finanzas/gastos_list.html'
    context_object_name = 'gastos'
    ordering = ['-fecha', '-id']

    def get_queryset(self):
        qs = super().get_queryset().select_related('deuda_relacionada')
        ver_todos = self.request.GET.get('ver_todos') == '1'
        if not ver_todos:
            qs = qs.filter(pagado=False)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ver_todos'] = self.request.GET.get('ver_todos') == '1'
        context['hoy'] = date.today()
        return context

    def post(self, request, *args, **kwargs):
        """
        Marca gastos como pagados según los checkboxes.

        Params:
            request (HttpRequest): incluye lista 'pagado' con ids marcados.
        """
        marcados = request.POST.getlist('pagado')
        Gasto.objects.update(pagado=False)
        if marcados:
            Gasto.objects.filter(pk__in=marcados).update(pagado=True)
        messages.success(request, 'Gastos actualizados.')
        return redirect('finanzas:lista_gastos')


class CrearGastoView(LoginRequiredMixin, CreateView):
    """
    Alta de gastos.

    Usa GastoForm para validar y mostrar el formulario.
    """
    model = Gasto
    form_class = GastoForm
    template_name = 'finanzas/gasto_form.html'
    success_url = reverse_lazy('finanzas:lista_gastos')

    def form_valid(self, form):
        messages.success(self.request, 'Gasto cargado correctamente.')
        return super().form_valid(form)


class EditarGastoView(LoginRequiredMixin, UpdateView):
    """
    Edición de gastos existentes.

    Params:
        pk (int): identificador del gasto a editar.
    """
    model = Gasto
    form_class = GastoForm
    template_name = 'finanzas/gasto_form.html'
    success_url = reverse_lazy('finanzas:lista_gastos')
    extra_context = {'form_title': 'Editar gasto'}

    def form_valid(self, form):
        messages.success(self.request, 'Gasto actualizado correctamente.')
        return super().form_valid(form)


class ListaDeudasView(LoginRequiredMixin, ListView):
    """
    Lista de deudas ordenadas por prioridad y entidad.
    """
    model = Deuda
    template_name = 'finanzas/deudas_list.html'
    context_object_name = 'deudas'
    ordering = ['prioridad', 'entidad__nombre']


@login_required
def importar_exportar(request):
    """
    Vista para importar/exportar CSV mediante management commands.

    Botones:
        - Exportar CSV: ejecuta exportar_csv y descarga un ZIP.
        - Importar CSV: sube uno o varios CSV, los guarda en imports/ y corre
          importar_csv.
    """
    exports_dir = Path('exports')
    imports_dir = Path('imports')

    if request.method == 'POST':
        if 'export' in request.POST:
            try:
                call_command('exportar_csv')
                csv_files = list(exports_dir.glob('*.csv'))
                if not csv_files:
                    messages.warning(request, 'No hay archivos CSV para exportar.')
                    return redirect('finanzas:importar_exportar')

                buffer = BytesIO()
                with ZipFile(buffer, 'w', ZIP_DEFLATED) as zipf:
                    for csv_file in csv_files:
                        zipf.write(csv_file, csv_file.name)
                buffer.seek(0)
                return FileResponse(buffer, as_attachment=True, filename='exports_csv.zip')
            except Exception as exc:  # noqa: BLE001
                messages.error(request, f'Error al exportar: {exc}')
                return redirect('finanzas:importar_exportar')

        if 'import' in request.POST:
            archivos = request.FILES.getlist('csv_files')
            if not archivos:
                messages.warning(request, 'Selecciona al menos un archivo CSV para importar.')
                return redirect('finanzas:importar_exportar')

            imports_dir.mkdir(parents=True, exist_ok=True)
            guardados = 0
            for file in archivos:
                if not file.name.lower().endswith('.csv'):
                    messages.warning(request, f'Se omitió {file.name} (no es CSV).')
                    continue
                destino = imports_dir / file.name
                with destino.open('wb') as dest:
                    for chunk in file.chunks():
                        dest.write(chunk)
                guardados += 1

            if guardados == 0:
                messages.warning(request, 'No se guardó ningún archivo válido para importar.')
                return redirect('finanzas:importar_exportar')

            try:
                call_command('importar_csv')
                messages.success(request, 'Importación completada.')
            except Exception as exc:  # noqa: BLE001
                messages.error(request, f'Error al importar: {exc}')
            return redirect('finanzas:importar_exportar')

    return render(request, 'finanzas/importar_exportar.html')
