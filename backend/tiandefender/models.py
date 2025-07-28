from django.db import models

# Create your models here.
class SecurityStatus(models.Model):
    component = models.CharField(max_length=100)  # e.g. Antivirus
    configured = models.IntegerField()
    needs_attention = models.IntegerField()

class ScoreHistory(models.Model):
    date = models.DateField()
    score = models.FloatField()

class LoginAlert(models.Model):
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.city}, {self.country} - {self.reason}"
