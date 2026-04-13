# app_escuela/api/views.py
from rest_framework.viewsets import ModelViewSet # type: ignore
from rest_framework.decorators import api_view, permission_classes # type: ignore
from rest_framework.permissions import IsAuthenticated, AllowAny # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework.authtoken.models import Token # pyright: ignore[reportMissingImports]
from django.contrib.auth import authenticate
from rest_framework.exceptions import ValidationError # type: ignore
from ..models import Matricula, Recibo, Usuario
from .serializers import MatriculaSerializer, ReciboSerializer, UserSerializer

PRECIO_MATRICULA = 6500


class MatriculaViewSet(ModelViewSet):
    queryset = Matricula.objects.all()  
    serializer_class = MatriculaSerializer
    permission_classes = [IsAuthenticated]


class ReciboViewSet(ModelViewSet):
    queryset = Recibo.objects.all()
    serializer_class = ReciboSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        matricula = serializer.validated_data['matricula']
        monto_pagado = serializer.validated_data['monto_pagado']
        
        recibos_existentes = Recibo.objects.filter(matricula=matricula)
        cantidad_pagos = recibos_existentes.count()
        total_pagado_anterior = sum(r.monto_pagado for r in recibos_existentes)
        
        if cantidad_pagos >= 2:
            raise ValidationError("Esta matrícula ya tiene los 2 pagos completos.")
        
        nuevo_total_pagado = total_pagado_anterior + monto_pagado
        if nuevo_total_pagado > matricula.monto_total:
            saldo_disponible = matricula.monto_total - total_pagado_anterior
            raise ValidationError(f"El monto excede el saldo pendiente. Saldo disponible: C${saldo_disponible:.2f}")
        
        if cantidad_pagos == 0:
            estado_recibo = 'anticipo'
        else:
            estado_recibo = 'pagado'
        
        serializer.save(estado=estado_recibo)
        
        matricula.monto_pagado = nuevo_total_pagado
        
        if nuevo_total_pagado >= matricula.monto_total:
            matricula.estado_pagado = 'pagado'
        elif nuevo_total_pagado > 0:
            matricula.estado_pagado = 'parcial'
        
        matricula.save()


class UserViewSet(ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'rol': user.rol,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name
        })
    return Response({'error': 'Credenciales inválidas'}, status=401)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def saldo(request):
    """Consultar saldo pendiente de una matrícula"""
    matricula_id = request.query_params.get('matricula')
    
    if not matricula_id:
        return Response({"error": "Se requiere el ID de la matrícula"}, status=400)
    
    try:
        matricula = Matricula.objects.get(id=matricula_id)
        recibos = matricula.recibos.all()
        
        total_pagado = sum(float(r.monto_pagado) for r in recibos)
        saldo_pendiente = float(matricula.monto_total - total_pagado)
        
        print(f"📊 Matrícula: {matricula.nombre} {matricula.apellido}")
        print(f"   Total: C${matricula.monto_total}")
        print(f"   Pagado: C${total_pagado}")
        print(f"   Saldo pendiente: C${saldo_pendiente}")
        print(f"   Cantidad pagos: {recibos.count()}")
        
        return Response({
            "monto_total": float(matricula.monto_total),
            "total_pagado": total_pagado,
            "saldo_pendiente": saldo_pendiente,
            "cantidad_pagos": recibos.count(),
            "pagos_permitidos": 2,
            "estado": matricula.estado_pagado,
            "tipo_pago": matricula.tipo_pago,
            "nombre": matricula.nombre,
            "apellido": matricula.apellido,
            "cedula": matricula.cedula,
            "precio_base": PRECIO_MATRICULA
        })
    except Matricula.DoesNotExist:
        return Response({"error": "Matrícula no encontrada"}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def precio_base(request):
    return Response({
        "precio_base": PRECIO_MATRICULA,
        "moneda": "C$",
        "descripcion": "Precio base de la matrícula"
    })