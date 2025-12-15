from django.contrib import admin

from .models import Entidad, Deuda, Ingreso, Gasto, Vencimiento


@admin.register(Entidad)
class EntidadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo')
    search_fields = ('nombre',)
    list_filter = ('tipo',)
    ordering = ('nombre',)


@admin.register(Deuda)
class DeudaAdmin(admin.ModelAdmin):
    list_display = (
        'entidad',
        'tipo_deuda',
        'monto_total',
        'pago_minimo',
        'fecha_vencimiento',
        'estado',
        'prioridad',
    )
    list_filter = ('tipo_deuda', 'estado', 'prioridad', 'entidad')
    search_fields = ('descripcion', 'entidad__nombre')
    ordering = ('prioridad', 'entidad__nombre')
    list_editable = ('estado', 'prioridad')
    fieldsets = (
        ('Datos básicos', {'fields': ('entidad', 'tipo_deuda', 'descripcion')}),
        ('Montos', {'fields': ('monto_total', 'pago_minimo', 'cuota_mensual_aprox', 'cuotas_restantes')}),
        ('Fechas', {'fields': ('fecha_vencimiento', 'proximo_pago')}),
        ('Estado', {'fields': ('estado', 'prioridad')}),
        ('Notas', {'fields': ('notas',)}),
    )


@admin.register(Ingreso)
class IngresoAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'tipo', 'descripcion', 'monto', 'confirmado')
    list_filter = ('tipo', 'confirmado', 'fecha')
    search_fields = ('descripcion',)
    ordering = ('-fecha', '-id')
    list_editable = ('confirmado',)
    fields = ('fecha', 'tipo', 'descripcion', 'monto', 'confirmado')


@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'tipo', 'categoria', 'descripcion', 'monto', 'pagado')
    list_filter = ('tipo', 'categoria', 'pagado', 'fecha')
    search_fields = ('descripcion', 'categoria')
    ordering = ('-fecha', '-id')
    list_editable = ('pagado',)
    fields = (
        'fecha',
        'tipo',
        'categoria',
        'descripcion',
        'monto',
        'pagado',
        'deuda_relacionada',
    )


@admin.register(Vencimiento)
class VencimientoAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'concepto', 'monto', 'estado', 'deuda')
    list_filter = ('estado', 'fecha')
    search_fields = ('concepto',)
    ordering = ('fecha', 'concepto')
    list_editable = ('estado',)
    fields = ('fecha', 'concepto', 'monto', 'estado', 'deuda', 'notas')
