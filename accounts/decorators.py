from functools import wraps
from django.http import HttpResponseForbidden

def requires_role(*roles):
    """
    Decorator que checa se user tem alguma das permissoes passadas como argumento.

    Args:
        *roles (str): Os roles que o usuário deve ter para acessar a view.

    Returns:
        function: A view original.

    Example:
        @requires_role('consultor', 'admin')
        def example_view(request):
            # View code
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if any(request.user.user_has_role(role) for role in roles) or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden('Você não tem permissão para acessar esta página')
        return _wrapped_view
    return decorator