# app_escuela/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('instructor', 'Instructor'),
        ('secretaria', 'Secretaria'),
        ('cajero', 'Cajero'),
        ('consulta', 'Solo Consulta'),
    )
    rol = models.CharField(max_length=20, choices=ROLES, default='consulta')
    
    def tiene_permiso(self, permiso):
        permisos = {
            'admin': ['*'],
            'secretaria': ['ver_matriculas', 'crear_matriculas', 'editar_matriculas', 
                          'ver_recibos', 'crear_recibos', 'exportar'],
            'cajero': ['ver_matriculas', 'ver_recibos', 'crear_recibos', 'editar_recibos', 'exportar'],
            'consulta': ['ver_matriculas', 'ver_recibos'],
            'instructor': ['ver_matriculas', 'ver_recibos']
        }
        
        if permiso in permisos.get(self.rol, []) or '*' in permisos.get(self.rol, []):
            return True
        return False

    def __str__(self):
        return f"{self.username} - {self.get_rol_display()}"


class Instructor(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, null=True, blank=True)
    especialidad = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.usuario.username if self.usuario else "Instructor sin usuario"


class Matricula(models.Model):
    PRECIO_BASE = 6500
    
    TIPO_PAGO_CHOICES = [
        ('pago_completo', 'Pago Completo'),
        ('Anticipo', 'Anticipo'),
        ('Beneficio', 'Beneficio'),
    ]

    TIPO_CURSO_CHOICES = [
        ('curso_completo', 'Completo'),
        ('Reforzamiento', 'Reforzamiento'),
    ]

    CATEGORIA_CHOICES = [
        ('A1', 'A1'),
        ('A2', 'A2'),
        ('A3', 'A3'),
    ]

    APARICIONIA_CHOICES = [
        ('Facebook', 'Facebook'),
        ('TikTok', 'TikTok'),
        ('Instagram', 'Instagram'),
        ('Referido', 'Referido'),
        ('Boletas', 'Boleta'),
        ('Amigo', 'Amigo'),
        ('otro', 'Otro'),
    ]

    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('Otro', 'Otro'),   
    ]
    
    ESTADO_PAGO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('parcial', 'Parcial'),
        ('pagado', 'Pagado'),
    ]

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    sexo = models.CharField(max_length=10, choices=SEXO_CHOICES)
    cedula = models.CharField(max_length=20, unique=True)
    direccion = models.CharField(max_length=200)
    correo_electronico = models.EmailField(unique=True)
    nivel_educativo = models.CharField(max_length=50)
    oficio = models.CharField(max_length=100)
    numero_telefono = models.CharField(max_length=20)
    fecha_nacimiento = models.DateField()
    grado = models.CharField(max_length=50)
    nombre_padre = models.CharField(max_length=100)
    n_emergencia = models.CharField(max_length=100)
    apariconia = models.CharField(max_length=100, choices=APARICIONIA_CHOICES)
    f_matricula = models.DateField(auto_now_add=True)
    categoria = models.CharField(max_length=50, choices=CATEGORIA_CHOICES)
    tipo_pago = models.CharField(max_length=50, choices=TIPO_PAGO_CHOICES)
    tipo_curso = models.CharField(max_length=50, choices=TIPO_CURSO_CHOICES)
    descripcion = models.TextField(blank=True, null=True)
    
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, default=PRECIO_BASE)
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado_pagado = models.CharField(max_length=20, choices=ESTADO_PAGO_CHOICES, default='pendiente')

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.cedula}"
    
    @property
    def saldo_pendiente(self):
        return self.monto_total - self.monto_pagado


class Recibo(models.Model):
    ESTADO_CHOICES = [
        ('pagado', 'Pagado'),
        ('anticipo', 'Anticipo')
    ]
    
    METODO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia Bancaria'),
        ('tarjeta', 'Tarjeta de Crédito/Débito'),
        ('cheque', 'Cheque'),
        ('otro', 'Otro'),
    ]

    matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE, related_name='recibos')
    numero_recibo = models.CharField(max_length=50, unique=True)
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES, default='efectivo')
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Recibo #{self.numero_recibo} - {self.matricula.nombre} - C${self.monto_pagado}"
     