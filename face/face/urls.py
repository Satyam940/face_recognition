from django.urls import path , include
from django.contrib import admin
from fr import views

urlpatterns = [
    path('admin/', admin.site.urls),
   
    path('', views.register_face, name='register_face'),
    path('recognize/', views.recognize_face, name='recognize_face'),

]
