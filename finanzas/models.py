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

    def __str__(self):
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

    def __str__(self):
        return f'{self.entidad} - {self.descripcion or self.get_tipo_deuda_display()}'


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

    def __str__(self):
        return f'{self.fecha} - {self.get_tipo_display()} - {self.monto}'


class Gasto(models.Model):
    TIPO_GASTO_CHOICES = [
        ('fijo', 'Fijo'),
        ('variable', 'Variable'),
        ('deuda', 'Deuda / cuota'),
        ('otro', 'Otro'),
    ]

    fecha = models.DateField()
    tipo = models.CharField(max_length=20, choices=TIPO_GASTO_CHOICES)
    categoria = models.CharField(
        max_length=50,
        help_text='Ej: alquiler, comida, colegio, nafta, servicios',
    )
    descripcion = models.CharField(max_length=255, blank=True)
    monto = models.DecimalField(max_digits=15, decimal_places=2)

    deuda_relacionada = models.ForeignKey(
        Deuda, null=True, blank=True, on_delete=models.SET_NULL,
        help_text='Si este gasto es el pago de una deuda, vinculalo acá.',
    )

    def __str__(self):
        return f'{self.fecha} - {self.categoria} - {self.monto}'


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

    def __str__(self):
        return f'{self.fecha} - {self.concepto} ({self.monto})'
