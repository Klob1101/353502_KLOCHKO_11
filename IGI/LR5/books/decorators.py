from functools import wraps
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
import logging

logger = logging.getLogger(__name__)

def api_login_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            logger.warning(f'Unauthorized API access attempt from {request.META.get("REMOTE_ADDR")}')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Authentication required'}, status=401)
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapped_view

def staff_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            logger.warning(f'Unauthorized staff access attempt from {request.META.get("REMOTE_ADDR")}')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Staff access required'}, status=403)
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapped_view 