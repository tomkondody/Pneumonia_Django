from django.db import models
from django.conf import settings
from django.utils import timezone

class Prediction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    result = models.CharField(max_length=20)
    confidence = models.FloatField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.result} ({self.confidence:.2f}%)"
