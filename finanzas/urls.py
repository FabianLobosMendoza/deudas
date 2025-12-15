from django.urls import path
from . import views

app_name = 'finanzas'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('deudas/', views.lista_deudas, name='lista_deudas'),
    path('vencimientos/', views.vencimientos, name='vencimientos'),
]
