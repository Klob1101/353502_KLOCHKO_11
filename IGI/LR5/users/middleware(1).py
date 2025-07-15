import pytz
from django.utils import timezone
from .models import UserSession

class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'timezone'):
            timezone.activate(pytz.timezone(request.user.timezone))
        else:
            timezone.deactivate()
        return self.get_response(request)

class SessionTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            session = UserSession.objects.create(user=request.user)
            request.session['current_session_id'] = session.id

        response = self.get_response(request)

        if request.user.is_authenticated and 'current_session_id' in request.session:
            try:
                session = UserSession.objects.get(id=request.session['current_session_id'])
                session.end_session()
                del request.session['current_session_id']
            except UserSession.DoesNotExist:
                pass

        return response 