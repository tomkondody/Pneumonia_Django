import os
import numpy as np
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from .models import Prediction

model = load_model(os.path.join(settings.BASE_DIR, "ml", "model.h5"))
IMG = (150,150)

@login_required
def user_dashboard(request):
    res = None
    conf = None

    if request.method == "POST" and "xray" in request.FILES:
        f = request.FILES["xray"]
        path = os.path.join(settings.MEDIA_ROOT, f.name)

        with open(path,"wb+") as dest:
            for chunk in f.chunks():
                dest.write(chunk)

        img = image.load_img(path, target_size=IMG)
        arr = image.img_to_array(img)
        arr = np.expand_dims(arr, 0)

        p = model.predict(arr)[0][0]
        res = "Pneumonia" if p>0.5 else "Normal"

        Prediction.objects.create(
            user=request.user,
            image=f.name,
            result=res,
            confidence=float(p)
        )

    return render(request,"user_dashboard.html",{"result":res,"confidence":conf})

@login_required
@user_passes_test(lambda u:u.role=="admin")
def admin_predictions(request):
    data = Prediction.objects.all().order_by("-created_at")
    return render(request,"admin_predictions.html",{"pred":data})
