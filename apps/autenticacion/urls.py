"""URLs del módulo de autenticación."""

from django.urls import path

from .views import (
    LoginView,
    LogoutView,
    RegistroClienteView,
    RegistroVendedorView,
    RenovacionTokenView,
)

urlpatterns = [
    # RF-AUT-001 (con y sin slash final para mayor tolerancia de clientes)
    path('auth/login', LoginView.as_view(), name='auth-login'),
    path('auth/login/', LoginView.as_view(), name='auth-login-slash'),
    # RF-AUT-002
    path('auth/register', RegistroClienteView.as_view(), name='auth-register'),
    path('auth/register/', RegistroClienteView.as_view(), name='auth-register-slash'),
    # RF-AUT-004 (rotación + lista negra configurada en settings)
    path('auth/refresh/', RenovacionTokenView.as_view(), name='auth-refresh'),
    # RF-AUT-005
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
    # RF-AUT-003 (Administrador)
    path('admin/vendedores/', RegistroVendedorView.as_view(), name='admin-vendedores'),
]
