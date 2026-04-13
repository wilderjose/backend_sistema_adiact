# app_escuela/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter # type: ignore
from .views import MatriculaViewSet, ReciboViewSet, UserViewSet, login, saldo, precio_base

router = DefaultRouter()
router.register(r'matricula', MatriculaViewSet)
router.register(r'recibo', ReciboViewSet)
router.register(r'usuarios', UserViewSet)

urlpatterns = [
    path('login/', login, name='login'),
    path('saldo/', saldo, name='saldo'),
    path('precio-base/', precio_base, name='precio_base'),
    path('', include(router.urls)),
]