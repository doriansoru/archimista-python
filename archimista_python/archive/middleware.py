"""Middleware che richiede autenticazione per tutte le pagine tranne login/logout."""

from django.shortcuts import redirect


class LoginRequiredMiddleware:
    """
    Richiede il login per tutte le URL tranne:
    - /login/
    - /logout/
    - /admin/
    - /static/
    - /media/
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip if user is already authenticated
        if request.user.is_authenticated:
            return self.get_response(request)

        # Paths that don't require authentication
        path = request.path_info.lstrip('/')

        # Allow access to auth, static, media, admin paths
        allowed_prefixes = [
            'login',
            'logout',
            'admin',
            'static',
            'media',
        ]

        for prefix in allowed_prefixes:
            if path == prefix or path == prefix + '/' or path.startswith(prefix + '/'):
                return self.get_response(request)

        return redirect('archive:login')
