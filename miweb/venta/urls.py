from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.user_login, name = 'login'),
    path('home/', views.home, name = 'home'),
    path('logout/', views.user_logout, name = 'logout'),
    #path('',views.home, name = 'home'), # pagina principal
    path('venta/q_cliente',views.consulta_clientes,name='lista_clientes'),
    path('venta/c_cliente',views.crear_cliente,name='crear_cliente'),
    path('venta/u_cliente',views.actualizar_cliente,name='actualizar_cliente'),  
    path('venta/d_cliente',views.borrar_cliente,name='borrar_cliente'),

    # Poner al final de la lista  
    re_path(r'^.*/$', views.handle_undefined_url, name = 'catch_all'),
]