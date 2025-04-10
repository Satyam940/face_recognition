from django.shortcuts import render
import json
import face_recognition
import numpy as np
import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import KnownFaceForm
from .models import KnownFace

def register_face(request):
    if request.method == 'POST':
        form = KnownFaceForm(request.POST,request.FILES)
        if form.is_valid():
            known_face = form.save(commit=False)
            image = face_recognition.load_image_file(known_face.image.path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_face.encoding = json.dumps(encodings[0].tolist())  # Save the encoding as JSON
                known_face.save()
                return render(request, 'fr/register_face.html', {'form': form, 'success': True})
            else:
                return render(request, 'fr/register_face.html', {'form': form, 'error': 'No face found in the image'})
    else:
        form = KnownFaceForm()
    return render(request, 'fr/register_face.html', {'form': form})

# Real-time Face Recognition View (using only face_recognition)
@csrf_exempt
def recognize_from_webcam(request):
    if request.method == 'POST':
        data_uri = request.POST.get('image')
        if not data_uri:
            return JsonResponse({'error': 'No image provided'}, status=400)

        # Decode base64 image
        header, encoded = data_uri.split(',', 1)
        img_data = base64.b64decode(encoded)

        # Load the image using face_recognition
        img = face_recognition.load_image_file(img_data)

        # Perform face recognition
        face_locations = face_recognition.face_locations(img)
        face_encodings = face_recognition.face_encodings(img, face_locations)

        known_faces = [np.array(json.loads(face.encoding)) for face in KnownFace.objects.all()]
        known_names = [{"name": face.name, "uid": face.uid, "class_name": face.class_name} for face in KnownFace.objects.all()]

        matches_info = []

        for encoding in face_encodings:
            matches = face_recognition.compare_faces(known_faces, encoding)
            if any(matches):
                best_match_idx = matches.index(True)
                matches_info.append(known_names[best_match_idx])

        return JsonResponse({'matches': matches_info})

    return JsonResponse({'error': 'Invalid request'}, status=405)