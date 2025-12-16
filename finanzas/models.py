from datetime import date

from django.db import models


class Entidad(models.Model):
    TIPO_CHOICES = [
        ('banco', 'Banco'),
        ('colegio', 'Colegio'),
        ('fintech', 'Fintech'),
        ('otro', 'Otro'),
    ]

    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='banco')

    class Meta:
        verbose_name = 'Entidad'
        verbose_name_plural = 'Entidades'
        ordering = ['nombre']

    def __str__(self) -> str:
        return self.nombre


class Deuda(models.Model):
    TIPO_DEUDA_CHOICES = [
        ('tarjeta', 'Tarjeta'),
        ('prestamo', 'Préstamo'),
        ('educacion', 'Educación'),
        ('servicio', 'Servicio'),
        ('otro', 'Otro'),
    ]

    PRIORIDAD_CHOICES = [
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja'),
    ]

    ESTADO_CHOICES = [
        ('al_dia', 'Al día'),
        ('en_curso', 'En curso'),
        ('en_mora', 'En mora'),
        ('cancelada', 'Cancelada'),
    ]

    entidad = models.ForeignKey(Entidad, on_delete=models.CASCADE)
    tipo_deuda = models.CharField(max_length=20, choices=TIPO_DEUDA_CHOICES)
    descripcion = models.CharField(max_length=255, blank=True)

    monto_total = models.DecimalField(max_digits=15, decimal_places=2)
    pago_minimo = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    fecha_vencimiento = models.DateField(null=True, blank=True)
    proximo_pago = models.DateField(null=True, blank=True)

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='al_dia',
    )

    prioridad = models.CharField(
        max_length=10,
        choices=PRIORIDAD_CHOICES,
        default='media',
    )

    cuota_mensual_aprox = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True
    )
    cuotas_restantes = models.PositiveIntegerField(null=True, blank=True)

    notas = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Deuda'
        verbose_name_plural = 'Deudas'
        ordering = ['prioridad', 'entidad__nombre']

    def __str__(self) -> str:
        return f'{self.entidad} - {self.get_tipo_deuda_display()}'

    @property
    def tipo_legible(self) -> str:
        """Devuelve el tipo de deuda en texto legible."""
        return self.get_tipo_deuda_display()


class Ingreso(models.Model):
    TIPO_INGRESO_CHOICES = [
        ('sueldo', 'Sueldo'),
        ('aguinaldo', 'Aguinaldo'),
        ('alquiler', 'Alquiler'),
        ('extra', 'Extraordinario'),
    ]

    fecha = models.DateField()
    tipo = models.CharField(max_length=20, choices=TIPO_INGRESO_CHOICES)
    descripcion = models.CharField(max_length=255, blank=True)
    monto = models.DecimalField(max_digits=15, decimal_places=2)
    confirmado = models.BooleanField(
        default=False,
        help_text='Marcar cuando el ingreso ya está cobrado.',
    )

    class Meta:
        verbose_name = 'Ingreso'
        verbose_name_plural = 'Ingresos'
        ordering = ['-fecha', '-id']

    def __str__(self) -> str:
        return f'{self.fecha} - {self.get_tipo_display()}'

    @property
    def dias_para_cobro(self) -> int | None:
        """Días hasta la fecha del ingreso (si sirve como fecha esperada)."""
        if not self.fecha:
            return None
        return (self.fecha - date.today()).days

    @property
    def estado_cobro(self) -> str:
        """Estado según fecha y si está confirmado."""
        if self.confirmado:
            return 'cobrado'
        if not self.fecha:
            return 'sin_fecha'
        dias = self.dias_para_cobro
        if dias is None:
            return 'sin_fecha'
        if dias < 0:
            return 'atrasado'
        if dias == 0:
            return 'hoy'
        return 'pendiente'


class Gasto(models.Model):
    TIPO_GASTO_CHOICES = [
        ('fijo', 'Fijo'),
        ('variable', 'Variable'),
        ('deuda', 'Deuda / cuota'),
        ('otro', 'Otro'),
    ]

    MEDIO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('debito', 'Debito'),
        ('tarjeta', 'Tarjeta'),
    ]

    fecha = models.DateField()
    tipo = models.CharField(max_length=20, choices=TIPO_GASTO_CHOICES)
    categoria = models.CharField(
        max_length=50,
        help_text='Ej: alquiler, comida, colegio, nafta, servicios',
    )
    descripcion = models.CharField(max_length=255, blank=True)
    monto = models.DecimalField(max_digits=15, decimal_places=2)
    pagado = models.BooleanField(
        default=False,
        help_text='Marcar cuando el gasto ya está pagado.',
    )
    medio_pago = models.CharField(
        max_length=20,
        choices=MEDIO_PAGO_CHOICES,
        default='efectivo',
        help_text='efectivo/debito descuentan ahora; tarjeta se descuenta al pagar.',
    )

    deuda_relacionada = models.ForeignKey(
        Deuda, null=True, blank=True, on_delete=models.SET_NULL,
        help_text='Si este gasto es el pago de una deuda, vinculalo acá.',
    )

    class Meta:
        verbose_name = 'Gasto'
        verbose_name_plural = 'Gastos'
        ordering = ['-fecha', '-id']

    def __str__(self) -> str:
        return f'{self.fecha} - {self.categoria}'

    @property
    def dias_para_vencer(self) -> int | None:
        """Días hasta la fecha del gasto (si se usa como vencimiento)."""
        if not self.fecha:
            return None
        return (self.fecha - date.today()).days

    @property
    def estado_vencimiento(self) -> str:
        """Estado según fecha y si está pagado."""
        if self.pagado:
            return 'pagado'
        if not self.fecha:
            return 'sin_fecha'
        dias = self.dias_para_vencer
        if dias is None:
            return 'sin_fecha'
        if dias < 0:
            return 'vencido'
        if dias == 0:
            return 'hoy'
        return 'por_vencer'

    @property
    def impacta_flujo(self) -> bool:
        """True si debe descontarse hoy del flujo (efectivo o debito)."""
        return self.medio_pago in ['efectivo', 'debito']


class Vencimiento(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
    ]

    fecha = models.DateField()
    concepto = models.CharField(max_length=255)
    monto = models.DecimalField(max_digits=15, decimal_places=2)

    deuda = models.ForeignKey(
        Deuda, null=True, blank=True, on_delete=models.SET_NULL,
        help_text='Vincular si corresponde a una deuda específica.',
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
    )
    notas = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Vencimiento'
        verbose_name_plural = 'Vencimientos'
        ordering = ['fecha', 'concepto']

    def __str__(self) -> str:
        return f'{self.fecha} - {self.concepto}'

    @property
    def esta_vencido(self) -> bool:
        """Indica si la fecha está vencida respecto de hoy."""
        return self.fecha < date.today() and self.estado != 'pagado'
