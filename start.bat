@echo off
setlocal

REM Activar entorno virtual si existe
if exist "venv\Scripts\activate.bat" call "venv\Scripts\activate.bat"

REM Configuracion de Postgres (ajusta estos valores a tu entorno local)
set POSTGRES_DB=deudas
set POSTGRES_USER=postgres
set POSTGRES_PASSWORD=postgres
set POSTGRES_HOST=localhost
set POSTGRES_PORT=5432

REM Iniciar el servidor en una ventana nueva
start "django-server" cmd /c "python manage.py runserver"

REM Dar un instante antes de abrir el navegador
timeout /t 2 /nobreak >nul

REM Abrir la página principal
start "" http://127.0.0.1:8000/

endlocal
