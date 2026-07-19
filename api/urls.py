from django.urls import path
from . import views

urlpatterns = [
    path('applications/', views.ApplicationListCreateAPIView.as_view(), name='api_applications_list'),
    path('applications/<str:app_id>/', views.ApplicationDetailAPIView.as_view(), name='api_applications_detail'),
    path('applications/<str:app_id>/analyze/', views.ResumeAnalyzeAPIView.as_view(), name='api_applications_analyze'),
]
