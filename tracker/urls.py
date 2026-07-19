from django.urls import path
from . import views

urlpatterns = [
    # Dashboard & Root
    path('', views.dashboard_view, name='dashboard'),
    path('analytics/', views.analytics_view, name='analytics'),
    
    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    
    # CRUD Applications
    path('application/add/', views.add_application_view, name='add_application'),
    path('application/<str:app_id>/', views.detail_application_view, name='detail_application'),
    path('application/<str:app_id>/edit/', views.edit_application_view, name='edit_application'),
    path('application/<str:app_id>/delete/', views.delete_application_view, name='delete_application'),
    
    # Reminders Scheduler
    path('reminders/', views.reminders_view, name='reminders'),
    path('reminders/trigger/', views.trigger_reminders_view, name='trigger_reminders'),
    
    # Custom Admin Dashboard
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-dashboard/users/', views.admin_users_view, name='admin_users'),
    path('admin-dashboard/users/<int:user_id>/toggle/', views.admin_toggle_user_status_view, name='admin_toggle_user_status'),
    path('admin-dashboard/applications/', views.admin_applications_view, name='admin_applications'),
]
