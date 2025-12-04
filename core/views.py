import os
import numpy as np
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from django.utils import timezone
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from .models import Prediction


# Load model once
MODEL_PATH = os.path.join(settings.BASE_DIR, "ml", "model.h5")
model = load_model(MODEL_PATH)
IMG_SIZE = (150, 150)


def is_admin(user):
    return user.is_authenticated and user.role == "admin"


def is_user(user):
    return user.is_authenticated and user.role == "user"


# ---------- USER DASHBOARD (PROTECTED) ----------
@login_required(login_url="login")
@user_passes_test(is_user, login_url="home")
def user_dashboard(request):
    result = None
    confidence = None

    if request.method == "POST" and "xray" in request.FILES:
        uploaded = request.FILES["xray"]
        path = os.path.join(settings.MEDIA_ROOT, uploaded.name)

        with open(path, "wb+") as dest:
            for chunk in uploaded.chunks():
                dest.write(chunk)

        img = image.load_img(path, target_size=IMG_SIZE)
        arr = image.img_to_array(img)
        arr = arr / 255.0
        arr = np.expand_dims(arr, axis=0)

        raw = float(model.predict(arr)[0][0])

        if raw >= 0.5:
            result = "Pneumonia"
            conf = raw
        else:
            result = "Normal"
            conf = 1 - raw

        confidence = round(conf * 100, 2)

        if os.path.exists(path):
            os.remove(path)

        Prediction.objects.create(
            user=request.user,
            result=result,
            confidence=confidence,
            created_at=timezone.now()
        )

    return render(request, "user_dashboard.html", {
        "result": result,
        "confidence": confidence
    })


# ---------- ADMIN PREDICTIONS (PROTECTED) ----------
@login_required(login_url="login")
@user_passes_test(is_admin, login_url="home")
def admin_predictions(request):
    data = Prediction.objects.all().order_by("-created_at")
    return render(request, "admin_predictions.html", {"pred": data})
