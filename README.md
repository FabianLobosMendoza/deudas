# Tablero Financiero (Django)

Aplicación web para organizar deudas, ingresos y gastos, con dashboard, carga rápida de datos y utilidades de importación/exportación CSV.

---

## Requisitos
- Python 3.12+
- pip
- git

---

## Instalación y arranque (Windows)
1. Clonar el repo  
   ```powershell
   git clone https://github.com/FabianLobosMendoza/deudas.git
   cd deudas
   ```
2. Crear y activar entorno  
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ``` 
   Si PowerShell bloquea scripts: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`.
3. Instalar dependencias  
   ```powershell
   pip install -r requirements.txt
   ```
4. Migraciones  
   ```powershell
   python manage.py makemigrations finanzas
   python manage.py migrate
   ```
5. Crear superusuario (opcional para admin)  
   ```powershell
   python manage.py createsuperuser
   ```
6. Levantar el servidor  
   ```powershell
   python manage.py runserver
   ```  
   (o usar tu `start.bat` si lo tienes).

---

## Uso principal
- Dashboard (`/`): resumen mensual (deuda total, cuotas, ingresos, gastos, saldo), relación cuotas/ingresos y tabla de **gastos por vencer** (no pagados dentro de 30 días).
- Ingresos (`/ingresos/`): listado con estado (pendiente, hoy, atrasado, cobrado) y switch para ver solo no cobrados o todos; check para marcar cobrado; botón para cargar nuevo ingreso.
- Gastos (`/gastos/`): listado con estado (por vencer, hoy, vencido, pagado) y switch para ver solo no pagados o todos; check para marcar pagado; botón para cargar nuevo gasto.
- Vencimientos: ya no se listan aparte en el dashboard; la lógica de “por vencer” se basa en gastos no pagados y su fecha.
- Deudas (`/deudas/`): listado de deudas.
- Login requerido para todas las vistas de datos.

---

## Importar / Exportar CSV (UI)
- Ruta: `/importar-exportar/`
- Exportar: botón que ejecuta `exportar_csv` y descarga un ZIP con todos los CSV (`exports/*.csv`).
- Importar: subir uno o varios CSV (entidades, deudas, ingresos, gastos, vencimientos); se guardan en `imports/` y luego se ejecuta `importar_csv`. Usa mensajes de estado (éxito/errores).

---

## Importar / Exportar CSV (commands)
- Exportar: `python manage.py exportar_csv` → genera CSV en `exports/`.
- Importar: `python manage.py importar_csv` → lee CSV desde `imports/`, crea/actualiza registros.
- Formato esperado (columnas en este orden):
  - `entidades.csv`: `nombre,tipo`
  - `deudas.csv`: `entidad,tipo_deuda,descripcion,monto_total,pago_minimo,fecha_vencimiento,proximo_pago,estado,prioridad,cuota_mensual_aprox,cuotas_restantes,notas`
  - `ingresos.csv`: `fecha,tipo,descripcion,monto,confirmado`
  - `gastos.csv`: `fecha,tipo,categoria,descripcion,monto,pagado,deuda_relacionada`
  - `vencimientos.csv`: `fecha,concepto,monto,deuda,estado,notas`

---

## Notas
- Config: `DEBUG` configurable por variable de entorno `DJANGO_DEBUG`; `ALLOWED_HOSTS` incluye localhost/127.0.0.1. Para producción, obtener `SECRET_KEY` y `DEBUG` desde entorno.
- Asegúrate de correr migraciones tras actualizar código.
- Usa el admin de Django (`/admin/`) si necesitas gestión avanzada (requiere superusuario).
