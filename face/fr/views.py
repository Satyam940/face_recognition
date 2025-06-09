from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import face_recognition
import base64
import json
import numpy as np
from PIL import Image
import io

from django.contrib.auth import logout
from django.contrib import messages

from .models import  KnownFace
from .forms import KnownFaceForm




def recognize_face(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            image_data = data.get('image_data')

            if not image_data:
                return JsonResponse({'status': 'fail', 'message': 'No image received'})

            image_data = image_data.split(',')[1]
            image = Image.open(io.BytesIO(base64.b64decode(image_data)))
            image_np = np.array(image)
            face_encodings = face_recognition.face_encodings(image_np)

            if not face_encodings:
                return JsonResponse({'status': 'fail', 'message': 'No face found'})

            input_encoding = face_encodings[0]

            for face in KnownFace.objects.all():
                known_encoding = np.array(json.loads(face.encoding))
                match = face_recognition.compare_faces([known_encoding], input_encoding)[0]

                if match:
                    # You can modify this logic as per your model design
                    return JsonResponse({
                        'status': 'success',
                        'name': face.name,
                        'uid': face.uid,
                        'class_name': face.class_name
                    })

            return JsonResponse({'status': 'fail', 'message': 'Face not recognized'})

        except Exception as e:
            return JsonResponse({'status': 'fail', 'message': str(e)})

    # If GET request, just render the page
    return render(request, 'recognize_face.html')













def register_face(request):
    if request.method == 'POST':
        form = KnownFaceForm(request.POST)
        if form.is_valid():
            face_entry = form.save(commit=False)
            image_data = request.POST.get('image_data')

            if image_data:
                # Decode and process the image in memory
                header, encoded = image_data.split(',', 1)
                img_data = base64.b64decode(encoded)
                image = face_recognition.load_image_file(io.BytesIO(img_data))
                encodings = face_recognition.face_encodings(image)

                if encodings:
                    face_entry.encoding = json.dumps(encodings[0].tolist())  # Store encoding only
                    face_entry.save()
                    return render(request, 'register_face.html', {'form': form, 'success': True})
                else:
                    return render(request, 'register_face.html', {'form': form, 'error': 'No face found'})
    
    else:
        form = KnownFaceForm()
    return render(request, 'register_face.html', {'form': form})

