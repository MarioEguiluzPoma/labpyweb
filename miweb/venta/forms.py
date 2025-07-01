from django import forms
#from django.core.validators import RegexValidator
# De nuestro negocio
from .models import Cliente
# Para gestionar un error
from django.core.exceptions import ValidationError

# Clase para crear un cliente
class ClienteCreateForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['id_cliente', 'ape_nom', 'fec_reg'] # Atributos del modelo cuyos valores se agregarán
        labels = {
            'id_cliente': 'DNI', 
            'ape_nom'   : 'Apellidos y Nombres',
            'fec_reg'   : 'Fecha de Registro',
        }
        widgets = {
            'fec_reg' : forms.DateInput(attrs={'type':'date'})  # es para poner un control de calendario
        }
        error_messages = {
            'id_cliente' : {
                'max_length' : "El DNI debe tener máximo 8 caracteres",
            }
        }

    def clean_id_cliente(self):
        # id_cliente viene de la plantilla (html)
        id_cliente = self.cleaned_data.get('id_cliente')

        if id_cliente:
            # Verificar que existe un DNI
            if Cliente.objects.filter(id_cliente=id_cliente).exists():
                # Realiza un lanzamiento de error 
                raise ValidationError("DNI_DUPLICADO")
            return id_cliente

# Clase para modificar un cliente
class ClienteUpdateForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['ape_nom', 'fec_reg'] # Atributos del modelo cuyos valores se agregarán
        labels = {
            #'id_cliente': 'DNI', 
            'ape_nom'   : 'Apellidos y Nombres',
            'fec_reg'   : 'Fecha de Registro',
        }

        widgets = {
            # 'id_cliente': forms.TextInput(
            #     attrs={
            #         'readonly':True,
            #         'class':'readonly-field'
            #     }
            # ),
            'ape_nom': forms.TextInput(
                attrs={
                    'placeholder':'Ingrese apellidos y nombres'
                }
            ),
            
            'fec_reg': forms.DateInput(
                attrs={
                    'type':'date'
                },
                format='%Y-%m-%d'
            )
                        
            # 'fec_reg': forms.DateInput(
            #     attrs={'type': 'date'}, 
            #     format=f'%d/%m/%Y'
            #     )                   
            
        }