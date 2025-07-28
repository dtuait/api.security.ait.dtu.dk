# tiandefender/views.py

from django.http import HttpResponse
from django.shortcuts import render
from .models import LoginAlert
import json

def hello_world(request):
    return HttpResponse("Hello from tiandefender! Stil working on it...")

def dashboard(request):
    alerts = LoginAlert.objects.all()
    alert_data = [
        {
            "city": a.city,
            "country": a.country,
            "latitude": a.latitude,
            "longitude": a.longitude,
            "timestamp": a.timestamp.strftime("%Y-%m-%d %H:%M"),
            "reason": a.reason
        }
        for a in alerts
    ]
    return render(request, 'tiandefender/dashboard.html', {'alerts_json': json.dumps(alert_data)})