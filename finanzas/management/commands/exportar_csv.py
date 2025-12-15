import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from finanzas.models import Entidad, Deuda, Ingreso, Gasto, Vencimiento


EXPORT_DIR = Path('exports')


def escribir_csv(nombre, columnas, rows):
    """Escribe un CSV en UTF-8 con las columnas y filas dadas."""
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    ruta = EXPORT_DIR / nombre
    with ruta.open('w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(columnas)
        for row in rows:
            writer.writerow(row)
    return ruta


class Command(BaseCommand):
    help = 'Exporta datos de finanzas a archivos CSV en la carpeta exports/'

    def handle(self, *args, **options):
        self.exportar_entidades()
        self.exportar_deudas()
        self.exportar_ingresos()
        self.exportar_gastos()
        self.exportar_vencimientos()

    def exportar_entidades(self):
        self.stdout.write('Exportando entidades...')
        columnas = ['nombre', 'tipo']
        rows = Entidad.objects.all().values_list('nombre', 'tipo')
        ruta = escribir_csv('entidades.csv', columnas, rows)
        self.stdout.write(f'Archivo {ruta} generado correctamente.')

    def exportar_deudas(self):
        self.stdout.write('Exportando deudas...')
        columnas = [
            'entidad',
            'tipo_deuda',
            'descripcion',
            'monto_total',
            'pago_minimo',
            'fecha_vencimiento',
            'proximo_pago',
            'estado',
            'prioridad',
            'cuota_mensual_aprox',
            'cuotas_restantes',
            'notas',
        ]
        rows = []
        for deuda in Deuda.objects.select_related('entidad'):
            rows.append([
                deuda.entidad.nombre if deuda.entidad else '',
                deuda.tipo_deuda,
                deuda.descripcion,
                deuda.monto_total,
                deuda.pago_minimo,
                deuda.fecha_vencimiento or '',
                deuda.proximo_pago or '',
                deuda.estado,
                deuda.prioridad,
                deuda.cuota_mensual_aprox or '',
                deuda.cuotas_restantes or '',
                deuda.notas or '',
            ])
        ruta = escribir_csv('deudas.csv', columnas, rows)
        self.stdout.write(f'Archivo {ruta} generado correctamente.')

    def exportar_ingresos(self):
        self.stdout.write('Exportando ingresos...')
        columnas = ['fecha', 'tipo', 'descripcion', 'monto', 'confirmado']
        rows = []
        for ing in Ingreso.objects.all():
            rows.append([
                ing.fecha,
                ing.tipo,
                ing.descripcion,
                ing.monto,
                ing.confirmado,
            ])
        ruta = escribir_csv('ingresos.csv', columnas, rows)
        self.stdout.write(f'Archivo {ruta} generado correctamente.')

    def exportar_gastos(self):
        self.stdout.write('Exportando gastos...')
        columnas = [
            'fecha',
            'tipo',
            'categoria',
            'descripcion',
            'monto',
            'pagado',
            'deuda_relacionada',
        ]
        rows = []
        for gasto in Gasto.objects.select_related('deuda_relacionada'):
            rows.append([
                gasto.fecha,
                gasto.tipo,
                gasto.categoria,
                gasto.descripcion,
                gasto.monto,
                gasto.pagado,
                gasto.deuda_relacionada.descripcion if gasto.deuda_relacionada else '',
            ])
        ruta = escribir_csv('gastos.csv', columnas, rows)
        self.stdout.write(f'Archivo {ruta} generado correctamente.')

    def exportar_vencimientos(self):
        self.stdout.write('Exportando vencimientos...')
        columnas = ['fecha', 'concepto', 'monto', 'deuda', 'estado', 'notas']
        rows = []
        for venc in Vencimiento.objects.select_related('deuda'):
            rows.append([
                venc.fecha,
                venc.concepto,
                venc.monto,
                venc.deuda.descripcion if venc.deuda else '',
                venc.estado,
                venc.notas or '',
            ])
        ruta = escribir_csv('vencimientos.csv', columnas, rows)
        self.stdout.write(f'Archivo {ruta} generado correctamente.')
