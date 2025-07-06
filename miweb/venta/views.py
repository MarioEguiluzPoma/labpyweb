from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
# En la vista se debe considera el modelo que se va usar
from .models import Cliente

def handle_undefined_url(request):
    '''
    Gestiona los urls que no estan definidos
    '''
    if not request.user.is_authenticated:
        messages.warning(request, 'Debe iniciar sesión para acceder al sistema')
        return redirect('login')
    else:
        messages.info(request, 'La página solicitada no existe. Se redirigirá al inicio')
    return redirect('home')

def user_login(request):
    # Si ya esta autenticado, enviarlo a home
    if request.user.is_authenticated:
        return redirect('home')
    
    # Si no está autenticado pedir usuario y clave
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username and password:
            user = authenticate(request, username=username, password=password)  
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Error de usuario o clave')
        else:
            messages.error(request, 'Ingrese los datos')

    # Si hay falla de autenticación, permitir reintentar
    return render(request, 'venta/login.html')


# Vista principal del sistema
@login_required
def home(request):
    # Obtener los permisos
    user_permissions = {
        'can_manage_clients' : (
            request.user.is_superuser or
            request.user.groups.filter(name='grp_cliente').exists() or
            request.user.has_perm('venta.add_cliente')
        ),
        'can_manage_products' : (
            request.user.is_superuser or
            request.user.groups.filter(name='grp_producto').exists()
        ),
         'can_manage_providers' : (
            request.user.is_superuser or
            request.user.groups.filter(name='grp_proveedor').exists()
        ),
        'is_admin' : request.user.is_superuser
    }

    context = {
        'user_permissions' : user_permissions,
        'user' : request.user
    }

    return render(request, 'venta/home.html', context)

# implementación de logout
def user_logout(request):
    logout(request)
    messages.success(request, 'Sesion cerrada correctamente')
    return redirect('login')

from django.http import HttpResponseForbidden

# consulta_clientes es la vista que muestra la lista
@login_required
@permission_required('venta.view_cliente', raise_exception=True)
def consulta_clientes(request):
    # verificar los permisos
    if not (request.user.is_superuser or
            request.user.groups.filter(name = 'grp_cliente').exists() or
            request.user.has_perm('venta.view_cliente')):
        return HttpResponseForbidden('No tiene permisos para ingresar aquí')

    # Se requiere obtner los datos a gestionar
    #clientes = Cliente.objects.all().order_by('ape_nom') # la data es la que se requiera 
    clientes = Cliente.objects.all().order_by('id_cliente') # la data es la que se requiera 
    # Estos datos deben estar disponibles para una plantilla (Template)
    # Se crea un diccionario llamado context (será accesible desde la plantilla)
    context = { # en el template será objetos y valores
        'clientes' : clientes,
        'titulo'   : 'Lista de Clientes',
        'mensaje'  : 'Hola'
    }
    # Se devolverá el enlace entre la plantilla y el contexto
    return render(request, 'venta\lista_clientes.html', context)

from .forms import ClienteCreateForm, ClienteUpdateForm
from django.contrib import messages
from django.shortcuts import redirect

@login_required
@permission_required('venta.add_cliente', raise_exception=True)
def crear_cliente(request):
    # Verificar los permisos
    if not (request.user.is_superuser or
            request.user.groups.filter(name = 'grp_cliente').exists() or
            request.user.has_perm('venta.add_cliente')
            ):
        return HttpResponseForbidden('No tiene permisos para crear cliente')
    dni_duplicado = False

    if request.method == 'POST':
        form = ClienteCreateForm(request.POST)
        if form.is_valid():
            form.save() # salvar los datos
            messages.success(request, 'Cliente registrado correctamente')
            print('Se guardó bien')
            return redirect('crear_cliente') # se redirecciona a la misma página
        else:
            if 'id_cliente' in form.errors:
                for error in form.errors['id_cliente']:
                    if str(error) == "DNI_DUPLICADO": # se recibe del raise de forms
                        dni_duplicado = True
                        # Limpiar los errores 
                        form.errors['id_cliente'].clear()
                        print('DNI Duplicado!')
                        break

    else:
        form = ClienteCreateForm() # No hace nada, devuelve la misma pantalla

    context = {
        'form':form,
        'dni_duplicado':dni_duplicado # Enviar el estado del dni duplicado
    }
    return render(request, 'venta/crear_cliente.html', context)    

@login_required
@permission_required('venta.change_cliente', raise_exception=True)
def actualizar_cliente(request):
    # Verificar los permisos del grupo
    if not (request.user.is_superuser or
            request.user.groups.filter(name = 'grp_cliente').exists() or
            request.user.has_perm('venta.change_cliente')
            ):
        return HttpResponseForbidden('No tiene permisos para modificar cliente')

    cliente = None
    dni_buscado = None
    form = None

    if request.method == 'POST':
        if 'buscar' in request.POST:
            # Buscar el cliente por DNI
            dni_buscado = request.POST.get('dni_busqueda')
            if dni_buscado:
                try: # intentar considerar la busqueda del cliente
                    # Obtener un objeto del tipo cliente
                    cliente = Cliente.objects.get(id_cliente=dni_buscado)
                    # Crear un formulario con los datos del objeto cliente
                    form = ClienteUpdateForm(instance=cliente)
                    messages.success(request, f'Cliente con DNI {dni_buscado} encontrado')
                except Cliente.DoesNotExist: # execepcion de dato no existente
                    messages.error(request, 'No se encontró Cliente con ese DNI')    
            else:
                messages.error(request, 'Por favor ingrese el DNI para buscar') 
        elif 'guardar' in request.POST:
            dni_buscado = request.POST.get('dni_busqueda') or request.POST.get('id_cliente')
            if dni_buscado:
                try:
                    cliente = Cliente.objects.get(id_cliente = dni_buscado)
                    form = ClienteUpdateForm(request.POST, instance=cliente)
                    if form.is_valid():
                        form.save()
                        messages.success(request, 'Cliente actualizado correctamente')
                        # formulario con datos actualizados
                        cliente.refresh_from_db()
                        # devolver al formulario
                        form = ClienteUpdateForm(instance=cliente)
                    else:
                        messages.error(request, 'Error en los datos del formulario')
                except Cliente.DoesNotExist:
                    messages.error(request, 'Cliente no encontrado')
                    

            else:
                messages.error(request, 'No se puede identificar al cliente para actaualizar')
    context = {
        'form':form,
        'dni_buscado': dni_buscado,
        'cliente_encontrado': cliente is not None,
        'cliente':cliente
    }
    return render(request,'venta/u_cliente.html', context)
                     
# Eliminar clientes
@login_required
@permission_required('venta.delete_cliente', raise_exception=True)
def borrar_cliente(request):
    # Verificar los permisos del grupo
    if not (request.user.is_superuser or
            request.user.groups.filter(name = 'grp_cliente').exists() or
            request.user.has_perm('venta.delete_cliente')
            ):
        return HttpResponseForbidden('No tiene permisos para eliminar cliente')


    clientes_encontrados = []
    tipo_busqueda = 'dni'
    termino_busqueda = '' # pa dentro de las cajas
    total_registros = 0

    if request.method == 'POST':
        #
        if 'consultar' in request.POST:
            # Realizar la búsqueda
            tipo_busqueda = request.POST.get('tipo_busqueda', 'dni')
            termino_busqueda = request.POST.get('termino_busqueda','').strip()

            if termino_busqueda:
                # procesar
                if tipo_busqueda == 'dni':
                    try:
                        cliente = Cliente.objects.get(id_cliente = termino_busqueda)
                        clientes_encontrados = [cliente]
                    except Cliente.DoesNotExist:
                        messages.error(request, 'No se encontró cliente con ese DNI')    

                elif tipo_busqueda == 'nombre':
                    clientes_encontrados = Cliente.objects.filter(
                        ape_nom__icontains = termino_busqueda # obtener las coincidencias
                    ).order_by('id_cliente') # debe estar ordenado

                    if not clientes_encontrados:
                        messages.error(request, 'No se encontraron clientes con ese nombre')

                total_registros = len(clientes_encontrados)

                if total_registros > 0:
                    messages.success(request, f'Se encontraron {total_registros} registro(s)')        

            else:
                messages.error(request, 'Ingrese un término de búsqueda')    

        elif 'eliminar' in request.POST:
            # Eliminar cliente
            dni_eliminar = request.POST.get('dni_eliminar')

            if dni_eliminar:
                try:
                    # buscar al cliente a eliminar
                    cliente = Cliente.objects.get(id_cliente = dni_eliminar)
                    cliente.delete()
                    messages.success(request, f'Cliente con DNI {dni_eliminar} eliminado correctamente')

                    # Volver a hacer la búsqueda para actualizar la lista
                    tipo_busqueda = request.POST.get('tipo_busqueda_actual', 'dni')
                    termino_busqueda = request.POST.get('termino_busqueda_actual','')

                    if termino_busqueda:
                        if tipo_busqueda == 'dni':
                            # Para DNI, no mostrar nada porque ya se eliminó
                            clientes_encontrados = []
                        elif tipo_busqueda == 'nombre':
                            # En este caso hay que buscar nuevamente lo que queda
                            clientes_encontrados = Cliente.objects.filter(
                                ape_nom__icontains = termino_busqueda
                            ).order_by('id_cliente')

                        total_registros = len(clientes_encontrados)
                

                except Cliente.DoesNotExist:
                    messages.error(request, 'Cliente no encontrado')
    
    context = {
        'clientes_encontrados' : clientes_encontrados,
        'tipo_busqueda' : tipo_busqueda,
        'termino_busqueda' : termino_busqueda,
        'total_registros' : total_registros
    }

    return render(request, 'venta/borrar_cliente.html', context)
