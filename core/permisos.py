"""Permisos por rol de la API (RNF-SEG-003)."""

from rest_framework.permissions import BasePermission


class _PermisoPorRol(BasePermission):
    rol_requerido = None
    message = 'No tiene permisos para realizar esta acción.'

    def has_permission(self, request, view):
        usuario = request.user
        return bool(
            usuario
            and usuario.is_authenticated
            and usuario.rol == self.rol_requerido
        )


class EsAdministrador(_PermisoPorRol):
    rol_requerido = 'Administrador'
    message = 'Se requiere el rol de Administrador.'


class EsVendedor(_PermisoPorRol):
    rol_requerido = 'Vendedor'
    message = 'Se requiere el rol de Vendedor.'


class EsCliente(_PermisoPorRol):
    rol_requerido = 'Cliente'
    message = 'Se requiere el rol de Cliente.'
