import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.management.base import BaseCommand

from finanzas.models import Entidad, Deuda, Ingreso, Gasto, Vencimiento


IMPORT_DIR = Path('imports')


def leer_csv(nombre, columnas):
    """Lee un CSV desde imports/ con encabezados exactos."""
    ruta = IMPORT_DIR / nombre
    try:
        with ruta.open('r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            if reader.fieldnames != columnas:
                raise ValueError(f'Columnas inválidas en {nombre}: {reader.fieldnames}')
            for row in reader:
                yield row
    except FileNotFoundError:
        yield from ()
    except ValueError as exc:
        print(f'Advertencia: {exc}')
        yield from ()


def parse_fecha(valor):
    if not valor:
        return None
    return datetime.strptime(valor, '%Y-%m-%d').date()


def parse_decimal(valor):
    if valor in (None, ''):
        return None
    try:
        return Decimal(valor)
    except InvalidOperation:
        raise ValueError(f'No se pudo parsear decimal: {valor}')


def parse_bool(valor):
    if isinstance(valor, bool):
        return valor
    return str(valor).strip().lower() in ('true', '1', 'sí', 'si')


class Command(BaseCommand):
    help = 'Importa datos desde archivos CSV en la carpeta imports/'

    def handle(self, *args, **options):
        self.importar_entidades()
        self.importar_deudas()
        self.importar_ingresos()
        self.importar_gastos()
        self.importar_vencimientos()

    def importar_entidades(self):
        print('Importando entidades...')
        columnas = ['nombre', 'tipo']
        for row in leer_csv('entidades.csv', columnas):
            nombre = row['nombre'].strip()
            tipo = row['tipo'].strip()
            obj, created = Entidad.objects.update_or_create(
                nombre=nombre,
                defaults={'tipo': tipo},
            )
            print(f"Entidad {'creada' if created else 'actualizada'}: {obj.nombre}")

    def importar_deudas(self):
        print('Importando deudas...')
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
        for row in leer_csv('deudas.csv', columnas):
            try:
                entidad_nombre = row['entidad'].strip()
                entidad = Entidad.objects.filter(nombre=entidad_nombre).first()
                descripcion = row['descripcion'].strip()
                obj, created = Deuda.objects.update_or_create(
                    descripcion=descripcion,
                    defaults={
                        'entidad': entidad,
                        'tipo_deuda': row['tipo_deuda'].strip(),
                        'monto_total': parse_decimal(row['monto_total']) or 0,
                        'pago_minimo': parse_decimal(row['pago_minimo']) or 0,
                        'fecha_vencimiento': parse_fecha(row['fecha_vencimiento']),
                        'proximo_pago': parse_fecha(row['proximo_pago']),
                        'estado': row['estado'].strip(),
                        'prioridad': row['prioridad'].strip(),
                        'cuota_mensual_aprox': parse_decimal(row['cuota_mensual_aprox']),
                        'cuotas_restantes': int(row['cuotas_restantes']) if row['cuotas_restantes'] else None,
                        'notas': row['notas'],
                    },
                )
                print(f"Deuda {'creada' if created else 'actualizada'}: {obj.descripcion}")
            except (ValueError, InvalidOperation) as exc:
                print(f'Advertencia: no se pudo importar deuda ({row}): {exc}')

    def importar_ingresos(self):
        print('Importando ingresos...')
        columnas = ['fecha', 'tipo', 'descripcion', 'monto', 'confirmado']
        for row in leer_csv('ingresos.csv', columnas):
            try:
                obj, created = Ingreso.objects.update_or_create(
                    descripcion=row['descripcion'],
                    fecha=parse_fecha(row['fecha']),
                    defaults={
                        'tipo': row['tipo'].strip(),
                        'monto': parse_decimal(row['monto']) or 0,
                        'confirmado': parse_bool(row['confirmado']),
                    },
                )
                print(f"Ingreso {'creado' if created else 'actualizado'}: {obj.descripcion}")
            except (ValueError, InvalidOperation) as exc:
                print(f'Advertencia: no se pudo importar ingreso ({row}): {exc}')

    def importar_gastos(self):
        print('Importando gastos...')
        columnas = ['fecha', 'tipo', 'categoria', 'descripcion', 'monto', 'pagado', 'deuda_relacionada']
        for row in leer_csv('gastos.csv', columnas):
            try:
                deuda_desc = row['deuda_relacionada'].strip()
                deuda = Deuda.objects.filter(descripcion=deuda_desc).first() if deuda_desc else None
                obj, created = Gasto.objects.update_or_create(
                    descripcion=row['descripcion'],
                    fecha=parse_fecha(row['fecha']),
                    defaults={
                        'tipo': row['tipo'].strip(),
                        'categoria': row['categoria'].strip(),
                        'monto': parse_decimal(row['monto']) or 0,
                        'pagado': parse_bool(row['pagado']),
                        'deuda_relacionada': deuda,
                    },
                )
                print(f"Gasto {'creado' if created else 'actualizado'}: {obj.descripcion}")
            except (ValueError, InvalidOperation) as exc:
                print(f'Advertencia: no se pudo importar gasto ({row}): {exc}')

    def importar_vencimientos(self):
        print('Importando vencimientos...')
        columnas = ['fecha', 'concepto', 'monto', 'deuda', 'estado', 'notas']
        for row in leer_csv('vencimientos.csv', columnas):
            try:
                deuda_desc = row['deuda'].strip()
                deuda = Deuda.objects.filter(descripcion=deuda_desc).first() if deuda_desc else None
                obj, created = Vencimiento.objects.update_or_create(
                    fecha=parse_fecha(row['fecha']),
                    concepto=row['concepto'],
                    defaults={
                        'monto': parse_decimal(row['monto']) or 0,
                        'deuda': deuda,
                        'estado': row['estado'].strip(),
                        'notas': row['notas'],
                    },
                )
                print(f"Vencimiento {'creado' if created else 'actualizado'}: {obj.concepto}")
            except (ValueError, InvalidOperation) as exc:
                print(f'Advertencia: no se pudo importar vencimiento ({row}): {exc}')
