"""URLs del módulo de usuarios."""

from django.urls import path

from .views import CambiarEstadoUsuarioView, ListaUsuariosView, PerfilView

urlpatterns = [
    # RF-USU-001 / RF-USU-002
    path('usuarios/perfil/', PerfilView.as_view(), name='usuarios-perfil'),
    # RF-USU-003 / RF-USU-004 (Administrador)
    path('admin/usuarios/', ListaUsuariosView.as_view(), name='admin-usuarios'),
    path(
        'admin/usuarios/<int:pk>/estado/',
        CambiarEstadoUsuarioView.as_view(),
        name='admin-usuario-estado',
    ),
]
