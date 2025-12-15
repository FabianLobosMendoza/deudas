from django.contrib import admin
from .models import Entidad, Deuda, Ingreso, Gasto, Vencimiento


@admin.register(Entidad)
class EntidadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo')
    search_fields = ('nombre',)


@admin.register(Deuda)
class DeudaAdmin(admin.ModelAdmin):
    list_display = (
        'entidad', 'tipo_deuda', 'descripcion',
        'monto_total', 'pago_minimo',
        'fecha_vencimiento', 'estado', 'prioridad',
    )
    list_filter = ('tipo_deuda', 'estado', 'prioridad', 'entidad')
    search_fields = ('descripcion', 'entidad__nombre')


@admin.register(Ingreso)
class IngresoAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'tipo', 'descripcion', 'monto')
    list_filter = ('tipo', 'fecha')
    search_fields = ('descripcion',)


@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'tipo', 'categoria', 'descripcion', 'monto')
    list_filter = ('tipo', 'categoria', 'fecha')
    search_fields = ('descripcion', 'categoria')


@admin.register(Vencimiento)
class VencimientoAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'concepto', 'monto', 'estado', 'deuda')
    list_filter = ('estado', 'fecha')
    search_fields = ('concepto',)
