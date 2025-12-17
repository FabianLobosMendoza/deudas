@echo off
setlocal

if exist "venv\Scripts\activate.bat" call "venv\Scripts\activate.bat"

REM Config Postgres
set POSTGRES_DB=deudas
set POSTGRES_USER=postgres
set POSTGRES_PASSWORD=postgres
set POSTGRES_HOST=localhost
set POSTGRES_PORT=5432

echo Migrando esquema...
python manage.py migrate || goto :error

echo Importando datos...
python manage.py loaddata dump.json || goto :error

echo Listo. Si necesitas admin: python manage.py createsuperuser
goto :eof

:error
echo Hubo un error durante la migracion.
exit /b 1
