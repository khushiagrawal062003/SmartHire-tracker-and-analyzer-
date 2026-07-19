from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_resume_view, name='upload_resume'),
    path('analyze/', views.analyze_resume_view, name='analyze_resume'),
]
