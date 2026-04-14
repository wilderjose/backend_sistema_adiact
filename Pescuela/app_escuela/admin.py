from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Instructor, Usuario, Matricula, Recibo

class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Información de Rol (ADIACT)', {'fields': ('rol',)}),
    )
    list_display = ['username', 'email', 'rol', 'is_staff']

admin.site.register(Matricula)
admin.site.register(Instructor)
admin.site.register(Recibo)
admin.site.register(Usuario, UsuarioAdmin)