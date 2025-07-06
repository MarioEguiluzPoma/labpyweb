from django.db import models

'''
  Definir la entidad (el nombre de la tabla y sus atributos (con tipos y validaciones))
  Cliente
     id_cliente, texto numérico de 8 caracteres, clave principal
     ape_nom, texto, max 80 caracteres
     fec_reg, Fecha (formato dd/mm/aaaa)
     fec_sis, Fecha y hora en que se registre el dato (timestamp)
'''
class Cliente(models.Model):
    # Creación de los atributos de Cliente
    id_cliente = models.CharField(primary_key=True, max_length=8, error_messages='El texto debe tener max 8 digitos')
    ape_nom = models.CharField(max_length=80)
    fec_reg = models.DateField() # solo es fecha
    fec_sis = models.DateTimeField(auto_now=True) # es fecha y hora actual

    def __str__(self):
        return f"Nombres : {self.ape_nom}, DNI : {self.id_cliente}"


'''
  Crear el modelo Producto
  Producto
     id_producto, numero entero autocorrelativo que comienza en 1, será clave principal
     nom_prod, texto de 50 caracteres como máximo
     des_prod, texto de 500 caracteres multilineas
     precio, numero real positivo de dos decimales
     stock, numero entero mayor o igual que cero
     activo, valor lógico (True si esta activo, de otra forma false)
     fec_vencim, tipo fecha (aaaa-mm-dd)
     fec_reg, tipo fecha y hora (registro del momento de guardado - timestamp)
'''  

'''
   Enviar al chat grupal la captura de la imagen de la tabla Producto en el Admin
   Pongan sus nombres y apellidos para reconocerlos
   https://chat.whatsapp.com/LirsKMPB8UAEkE6ZfqJQnA

   Puntaje: 7 puntos para la nota 1
   Plazo: 12/06/2025 23:59 hrs
'''  
from django.core.validators import MinValueValidator

class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)  # entero autocorrelativo, clave primaria
    nom_prod = models.CharField(max_length=50)
    des_prod = models.TextField(max_length=500)
    precio = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    stock = models.PositiveIntegerField()  # entero >= 0
    activo = models.BooleanField(default=True)
    fec_vencim = models.DateField()
    fec_reg = models.DateTimeField(auto_now_add=True)  # timestamp al guardar

    def __str__(self):
        return f'{self.id_producto} - {self.nom_prod} - {self.precio}' 

'''
class Venta(models.Model):
    id_venta = models.AutoField(primary_key=True)
    id_producto = models.ForeignKey(name='Producto')
'''        
from django.db import models

class Venta(models.Model):
    id_venta = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE)
    id_producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Venta {self.id_venta} - Cliente: {self.id_cliente} - Producto: {self.id_producto}"