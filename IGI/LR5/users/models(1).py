from django.contrib.auth.models import AbstractUser
from django.db import models
import pytz
from django.conf import settings
from django.utils import timezone
from statistics import median

TIMEZONE_CHOICES = [(tz, tz) for tz in pytz.all_timezones]

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    license_number = models.CharField(max_length=50, blank=True)
    timezone = models.CharField(max_length=50, choices=TIMEZONE_CHOICES, default='UTC')
    
    def __str__(self):
        return self.username 

class UserSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)

    def end_session(self):
        if not self.end_time:
            self.end_time = timezone.now()
            self.duration = self.end_time - self.start_time
            self.save()

    @classmethod
    def get_median_duration(cls, start_date=None, end_date=None):
        sessions = cls.objects.filter(duration__isnull=False)
        if start_date:
            sessions = sessions.filter(start_time__gte=start_date)
        if end_date:
            sessions = sessions.filter(end_time__lte=end_date)
        
        durations = [session.duration.total_seconds() for session in sessions]
        return median(durations) if durations else None

    def __str__(self):
        return f"Session for {self.user.username} from {self.start_time}" 