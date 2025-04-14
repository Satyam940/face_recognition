from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import face_recognition
import json
import base64
from .forms import KnownFaceForm
from .models import KnownFace
from PIL import Image
import io
import numpy as np
from PIL import Image, ExifTags

def register_face(request):
    if request.method == 'POST':
        form = KnownFaceForm(request.POST)
        if form.is_valid():
            # Create an entry with the provided details (name, uid, class)
            known_face = form.save(commit=False)

            # Capture the image and process it
            image_data = request.POST.get('image_data')  # Get the base64 image data from the form
            if image_data:
                header, encoded = image_data.split(',', 1)
                img_data = base64.b64decode(encoded)

                # Create the image file to save (this step is required because ImageField expects a file)
                with open("temp_image.jpg", "wb") as f:
                    f.write(img_data)

                # Load image using face_recognition library
                image = face_recognition.load_image_file("temp_image.jpg")
                encodings = face_recognition.face_encodings(image)

                if encodings:
                    # Save the face encoding as JSON
                    known_face.encoding = json.dumps(encodings[0].tolist())
                    known_face.image = "temp_image.jpg"  # Save the captured image
                    known_face.save()

                    return render(request, 'fr/register_face.html', {'form': form, 'success': True})
                else:
                    return render(request, 'fr/register_face.html', {'form': form, 'error': 'No face found in the image'})

            return render(request, 'fr/register_face.html', {'form': form, 'error': 'No image captured'})
    else:
        form = KnownFaceForm()

    return render(request, 'fr/register_face.html', {'form': form})

def auto_rotate_image(file_path):
    """Rotate image if it has EXIF orientation (phones often add this)."""
    try:
        image = Image.open(file_path)
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break

        exif = image._getexif()
        if exif and orientation in exif:
            if exif[orientation] == 3:
                image = image.rotate(180, expand=True)
            elif exif[orientation] == 6:
                image = image.rotate(270, expand=True)
            elif exif[orientation] == 8:
                image = image.rotate(90, expand=True)
        image.save(file_path)
    except Exception as e:
        print("EXIF rotation skipped:", e)

@csrf_exempt
def recognize_face(request):
    if request.method == 'GET':
        return render(request, 'fr/recognize_face.html')  # load webcam page on GET

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            image_data = data.get('image_data')

            if not image_data:
                return JsonResponse({'status': 'fail', 'message': 'No image received'}, status=400)

            # Decode base64 image
            image_data = image_data.split(',')[1]
            image = Image.open(io.BytesIO(base64.b64decode(image_data)))
            image_np = np.array(image)

            # Get face encodings
            face_encodings = face_recognition.face_encodings(image_np)

            if not face_encodings:
                return JsonResponse({'status': 'fail', 'message': 'No face found in image'}, status=400)

            input_encoding = face_encodings[0]

            for face in KnownFace.objects.all():
                known_encoding = np.array(json.loads(face.encoding))
                match = face_recognition.compare_faces([known_encoding], input_encoding)[0]

                if match:
                    return JsonResponse({
                        'status': 'success',
                        'name': face.name,
                        'uid': face.uid,
                        'class_name': face.class_name
                    })

            return JsonResponse({'status': 'fail', 'message': 'Face not recognized'}, status=404)

        except Exception as e:
            return JsonResponse({'status': 'fail', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'fail', 'message': 'Only POST method allowed'}, status=405)