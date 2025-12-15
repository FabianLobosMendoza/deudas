from django.urls import path

from . import views

app_name = 'finanzas'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('deudas/', views.ListaDeudasView.as_view(), name='lista_deudas'),
    path('ingresos/', views.ListaIngresosView.as_view(), name='lista_ingresos'),
    path('gastos/', views.ListaGastosView.as_view(), name='lista_gastos'),
    path('ingresos/nuevo/', views.CrearIngresoView.as_view(), name='nuevo_ingreso'),
    path('ingresos/<int:pk>/editar/', views.EditarIngresoView.as_view(), name='editar_ingreso'),
    path('gastos/nuevo/', views.CrearGastoView.as_view(), name='nuevo_gasto'),
    path('gastos/<int:pk>/editar/', views.EditarGastoView.as_view(), name='editar_gasto'),
    path('importar-exportar/', views.importar_exportar, name='importar_exportar'),
]
