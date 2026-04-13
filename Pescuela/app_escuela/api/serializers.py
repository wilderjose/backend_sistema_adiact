# app_escuela/api/serializers.py
from rest_framework import serializers # type: ignore
from ..models import Matricula, Recibo, Usuario

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'rol', 'password']
        extra_kwargs = {'password': {'write_only': True, 'required': False}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = Usuario(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class MatriculaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Matricula
        fields = '__all__'


class ReciboSerializer(serializers.ModelSerializer):
    matricula_data = MatriculaSerializer(source='matricula', read_only=True)
    estudiante_nombre = serializers.SerializerMethodField()
    estudiante_cedula = serializers.SerializerMethodField()
    
    class Meta:
        model = Recibo
        fields = '__all__'
    
    def get_estudiante_nombre(self, obj):
        return f"{obj.matricula.nombre} {obj.matricula.apellido}"
    
    def get_estudiante_cedula(self, obj):
        return obj.matricula.cedula