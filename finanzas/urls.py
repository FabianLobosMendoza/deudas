from django.urls import path

from . import views

app_name = 'finanzas'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('deudas/', views.ListaDeudasView.as_view(), name='lista_deudas'),
    path('vencimientos/', views.ListaVencimientosView.as_view(), name='vencimientos'),
    path('ingresos/', views.ListaIngresosView.as_view(), name='lista_ingresos'),
    path('gastos/', views.ListaGastosView.as_view(), name='lista_gastos'),
    path('ingresos/nuevo/', views.CrearIngresoView.as_view(), name='nuevo_ingreso'),
    path('gastos/nuevo/', views.CrearGastoView.as_view(), name='nuevo_gasto'),
    path('vencimientos/nuevo/', views.CrearVencimientoView.as_view(), name='nuevo_vencimiento'),
]
