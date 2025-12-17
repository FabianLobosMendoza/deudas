# Tablero Financiero (Django)

Aplicacion web para organizar deudas, ingresos y gastos, con dashboard, carga rapida de datos y utilidades de importacion/exportacion CSV.

---

## Requisitos
- Python 3.12+
- pip
- git

---

## Instalacion y arranque (Windows)
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
- Dashboard (`/`): resumen mensual (deuda total, cuotas, ingresos, gastos, saldo), relacion cuotas/ingresos y tabla de **gastos por vencer** (no pagados dentro de 30 dias).
- Ingresos (`/ingresos/`): listado con estado (pendiente, hoy, atrasado, cobrado) y switch para ver solo no cobrados o todos; check para marcar cobrado; boton para cargar nuevo ingreso.
- Gastos (`/gastos/`): listado con estado (por vencer, hoy, vencido, pagado) y switch para ver solo no pagados o todos; check para marcar pagado; boton para cargar nuevo gasto.
- Vencimientos: ya no se listan aparte en el dashboard; la logica de "por vencer" se basa en gastos no pagados y su fecha.
- Deudas (`/deudas/`): listado de deudas.
- Login requerido para todas las vistas de datos.

---

## Importar / Exportar CSV (UI)
- Ruta: `/importar-exportar/`
- Exportar: boton que ejecuta `exportar_csv` y descarga un ZIP con todos los CSV (`exports/*.csv`).
- Importar: subir uno o varios CSV (entidades, deudas, ingresos, gastos, vencimientos); se guardan en `imports/` y luego se ejecuta `importar_csv`. Usa mensajes de estado (exito/errores).

---

## Importar / Exportar CSV (commands)
- Exportar: `python manage.py exportar_csv` genera CSV en `exports/`.
- Importar: `python manage.py importar_csv` lee CSV desde `imports/`, crea/actualiza registros.
- Formato esperado (columnas en este orden):
  - `entidades.csv`: `nombre,tipo`
  - `deudas.csv`: `entidad,tipo_deuda,descripcion,monto_total,pago_minimo,fecha_vencimiento,proximo_pago,estado,prioridad,cuota_mensual_aprox,cuotas_restantes,notas`
  - `ingresos.csv`: `fecha,tipo,descripcion,monto,confirmado`
  - `gastos.csv`: `fecha,tipo,categoria,descripcion,monto,pagado,deuda_relacionada`
  - `vencimientos.csv`: `fecha,concepto,monto,deuda,estado,notas`

---

## Notas
- Config: `DEBUG` configurable por variable de entorno `DJANGO_DEBUG`; `ALLOWED_HOSTS` incluye localhost/127.0.0.1. Para produccion, obtener `SECRET_KEY` y `DEBUG` desde entorno.
- Asegurate de correr migraciones tras actualizar codigo.
- Usa el admin de Django (`/admin/`) si necesitas gestion avanzada (requiere superusuario).

---

## Deploy en Render (SQLite, sin Postgres)
- Render usa un disco efimero: cada redeploy borra el `db.sqlite3`. Adecuado solo para pruebas/demo, no para produccion.
1. Usa `render.yaml` para crear el servicio web (Blueprint):
   - `buildCommand`: instala dependencias y ejecuta `collectstatic --noinput`.
   - `startCommand`: `gunicorn config.wsgi:application --bind 0.0.0.0:8000`.
   - `migrateCommand`: `python manage.py migrate --noinput` (crea/actualiza `db.sqlite3` en el disco efimero).
2. Variables necesarias:
   - `DJANGO_SECRET_KEY` (sync: false).
   - `DJANGO_DEBUG=False`.
   - `PYTHON_VERSION=3.12`.
3. Render setea `RENDER_EXTERNAL_HOSTNAME` automaticamente; se usa en `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS`.
