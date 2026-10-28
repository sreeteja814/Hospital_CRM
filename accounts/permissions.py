from functools import wraps
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if request.user.is_superuser or request.user.role in roles:
                return view_func(request, *args, **kwargs)
            return render(request, '403.html', {'needed_roles': roles}, status=403)
        return _wrapped
    return decorator
