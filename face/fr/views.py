from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import face_recognition
import json
import base64
from .forms import KnownFaceForm
from .models import KnownFace

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

def recognize_face(request):
    if request.method == 'POST':
        try:
            # Load and decode the image
            data = json.loads(request.body)
            image_data = data.get('image_data')

            if not image_data:
                return JsonResponse({'status': 'fail', 'message': 'No image data'})

            # Decode the base64 image
            header, encoded = image_data.split(',', 1)
            img_data = base64.b64decode(encoded)

            # Save the image temporarily
            with open("temp_recog.jpg", "wb") as f:
                f.write(img_data)

            # Use face_recognition to find face encodings
            image = face_recognition.load_image_file("temp_recog.jpg")
            encodings = face_recognition.face_encodings(image)

            if not encodings:
                return JsonResponse({'status': 'fail', 'message': 'No face found in the image'})

            captured_encoding = encodings[0]

            # Compare the captured encoding with stored known encodings
            for known in KnownFace.objects.all():
                known_encoding = np.array(json.loads(known.encoding))
                match = face_recognition.compare_faces([known_encoding], captured_encoding)[0]

                if match:
                    return JsonResponse({
                        'status': 'success',
                        'name': known.name,
                        'uid': known.uid,
                        'class_name': known.class_name,
                    })

            return JsonResponse({'status': 'fail', 'message': 'No match found'})

        except Exception as e:
            # Log the error
            print(f"Error: {str(e)}")
            return JsonResponse({'status': 'fail', 'message': 'An error occurred: ' + str(e)})

    return JsonResponse({'status': 'fail', 'message': 'Only POST method is allowed'})