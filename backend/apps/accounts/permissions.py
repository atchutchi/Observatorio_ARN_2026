from rest_framework.permissions import BasePermission


class IsARNAdmin(BasePermission):
    """Apenas administradores ARN"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_arn_admin


class IsARNStaff(BasePermission):
    """Administradores e analistas ARN"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_arn_staff


class IsOperatorUser(BasePermission):
    """Utilizadores de operador (Telecel, Orange, Starlink)"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_operator_user


class IsOwnerOrARN(BasePermission):
    """
    Operador só acede aos seus dados. ARN acede a tudo.
    Objects must have an 'operator' attribute.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_arn_staff:
            return True
        if request.user.is_operator_user and hasattr(obj, 'operator'):
            return obj.operator == request.user.operator
        return False
