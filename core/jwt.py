"""Serializador JWT personalizado: agrega rol, email y comercio_id al payload.

Contenido del JWT según el rol (RF-AUT-001):
- Administrador y Cliente: user_id, email, rol.
- Vendedor: además comercio_id asociado.
"""

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class TokenConRolSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['rol'] = user.rol
        if user.rol == user.Rol.VENDEDOR:
            comercio = getattr(user, 'comercio', None)
            if comercio is not None:
                token['comercio_id'] = comercio.id
        return token
