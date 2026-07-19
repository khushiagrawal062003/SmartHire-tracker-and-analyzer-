from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as django_login, logout as django_logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .db import (
    create_application,
    get_application_by_id,
    update_application,
    delete_application,
    list_applications,
    get_metrics_summary,
    admin_list_applications,
    admin_get_metrics_summary
)
from .forms import JobApplicationForm
from .scheduler import start_reminder_scheduler

@login_required(login_url='login')
def dashboard_view(request):
    """
    Renders the applications list, incorporating search and filtering.
    Iterates through MongoDB cursor results.
    """
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    user_id = request.user.id
    
    try:
        # Fetch applications and metrics from MongoDB
        applications = list_applications(
            user_id=user_id,
            search_query=search_query,
            status_filter=status_filter
        )
        counts = get_metrics_summary(user_id=user_id)
    except ConnectionError as e:
        messages.error(request, str(e))
        applications = []
        counts = {"total": 0, "applied": 0, "interviewing": 0, "offered": 0, "rejected": 0}
        
    context = {
        "applications": applications,
        "counts": counts,
        "search_query": search_query,
        "status_filter": status_filter,
    }
    return render(request, 'tracker/dashboard.html', context)

def login_view(request):
    """
    Handles user login using Django's session authentication (SQLite backstore).
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not username or not password:
            messages.error(request, "Please fill in all fields.")
            return render(request, 'tracker/login.html')
            
        user = authenticate(request, username=username, password=password)
        if user is not None:
            django_login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
        else:
            # Check if user exists. If not, auto-create them (friendly beginner dev mode workflow)
            try:
                if not User.objects.filter(username=username).exists():
                    user = User.objects.create_user(username=username, password=password)
                    django_login(request, user)
                    messages.success(request, f"Welcome to SmartHire, {user.username}! Your account has been auto-created.")
                    return redirect('dashboard')
                else:
                    messages.error(request, "Incorrect password for this user.")
            except Exception as e:
                messages.error(request, f"Authentication error: {e}")
                
    return render(request, 'tracker/login.html')

def logout_view(request):
    """
    Logs out the user session.
    """
    django_logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('login')

def register_view(request):
    """
    Handles user signup and registers session details.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        
        if not username or not email or not password:
            messages.error(request, "All fields are required.")
            return render(request, 'tracker/register.html')
            
        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, 'tracker/register.html')
            
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'tracker/register.html')
            
        try:
            # Create user in SQLite database
            user = User.objects.create_user(username=username, email=email, password=password)
            django_login(request, user)
            messages.success(request, f"Registration successful! Welcome, {user.username}!")
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f"Registration failed: {e}")
            
    return render(request, 'tracker/register.html')

@login_required(login_url='login')
def add_application_view(request):
    """
    Displays the application creation form and inserts it to MongoDB.
    """
    if request.method == "POST":
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            try:
                # Save input data to MongoDB
                create_application(
                    user_id=request.user.id,
                    company_name=form.cleaned_data['company_name'],
                    job_title=form.cleaned_data['job_title'],
                    status=form.cleaned_data['status'],
                    salary=form.cleaned_data['salary'],
                    deadline=str(form.cleaned_data['deadline']) if form.cleaned_data['deadline'] else '',
                    contact_email=form.cleaned_data['contact_email'],
                    description=form.cleaned_data['description']
                )
                messages.success(request, "Job application successfully added to MongoDB tracker.")
                return redirect('dashboard')
            except ConnectionError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, "Form validation failed. Please check your entries.")
    else:
        form = JobApplicationForm()
        
    return render(request, 'tracker/add_application.html', {"form": form})

@login_required(login_url='login')
def detail_application_view(request, app_id):
    """
    Displays detail card of a specific job application from MongoDB.
    """
    try:
        app = get_application_by_id(app_id, user_id=request.user.id)
        if not app:
            messages.error(request, "Job application not found.")
            return redirect('dashboard')
    except ConnectionError as e:
        messages.error(request, str(e))
        return redirect('dashboard')
        
    return render(request, 'tracker/detail_application.html', {"app": app})

@login_required(login_url='login')
def edit_application_view(request, app_id):
    """
    Pre-populates application information and updates MongoDB document.
    """
    try:
        app = get_application_by_id(app_id, user_id=request.user.id)
        if not app:
            messages.error(request, "Job application not found.")
            return redirect('dashboard')
    except ConnectionError as e:
        messages.error(request, str(e))
        return redirect('dashboard')
        
    if request.method == "POST":
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            update_fields = {
                "company_name": form.cleaned_data['company_name'],
                "job_title": form.cleaned_data['job_title'],
                "status": form.cleaned_data['status'],
                "salary": form.cleaned_data['salary'],
                "deadline": str(form.cleaned_data['deadline']) if form.cleaned_data['deadline'] else '',
                "contact_email": form.cleaned_data['contact_email'],
                "description": form.cleaned_data['description']
            }
            try:
                update_application(app_id, user_id=request.user.id, update_fields=update_fields)
                messages.success(request, "Job application details updated successfully.")
                return redirect('detail_application', app_id=app_id)
            except ConnectionError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, "Form validation failed.")
    else:
        # Prepopulate Django form from MongoDB document data
        initial_data = {
            "company_name": app.get('company_name'),
            "job_title": app.get('job_title'),
            "status": app.get('status'),
            "salary": app.get('salary'),
            "deadline": app.get('deadline') if app.get('deadline') else None,
            "contact_email": app.get('contact_email'),
            "description": app.get('description')
        }
        form = JobApplicationForm(initial=initial_data)
        
    return render(request, 'tracker/edit_application.html', {"form": form, "app": app})

@login_required(login_url='login')
def delete_application_view(request, app_id):
    """
    Confirms and deletes job application from MongoDB.
    """
    try:
        app = get_application_by_id(app_id, user_id=request.user.id)
        if not app:
            messages.error(request, "Job application not found.")
            return redirect('dashboard')
    except ConnectionError as e:
        messages.error(request, str(e))
        return redirect('dashboard')
        
    if request.method == "POST":
        try:
            delete_application(app_id, user_id=request.user.id)
            messages.warning(request, f"Successfully removed {app['company_name']} application.")
            return redirect('dashboard')
        except ConnectionError as e:
            messages.error(request, str(e))
            
    return render(request, 'tracker/delete_application.html', {"app": app})

@login_required(login_url='login')
def reminders_view(request):
    """
    Lists applications containing deadline notifications.
    """
    user_id = request.user.id
    try:
        applications = list_applications(user_id=user_id)
        applications_with_deadlines = [a for a in applications if a.get('deadline')]
    except ConnectionError as e:
        messages.error(request, str(e))
        applications_with_deadlines = []
        
    return render(request, 'tracker/reminders.html', {"applications_with_deadlines": applications_with_deadlines})

@login_required(login_url='login')
def trigger_reminders_view(request):
    """
    Action endpoint: Spawns a background thread to process follow-up deadline alarms
    without blocking web-server.
    """
    if request.method == "POST":
        # Launch multithreading task scheduler
        start_reminder_scheduler(request.user.id, request.user.username)
        messages.info(
            request,
            "Background reminder scheduler thread launched successfully! "
            "Scan output and deadline alerts are printed in the terminal logs."
        )
    return redirect('reminders')

@login_required(login_url='login')
def analytics_view(request):
    """
    Renders a dedicated page for visual analytics and metrics summary.
    """
    user_id = request.user.id
    try:
        counts = get_metrics_summary(user_id=user_id)
    except ConnectionError as e:
        messages.error(request, str(e))
        counts = {"total": 0, "applied": 0, "interviewing": 0, "offered": 0, "rejected": 0}
        
    return render(request, 'tracker/analytics.html', {"counts": counts})

def staff_required(view_func):
    """
    Decorator that checks if the logged in user is staff.
    """
    @login_required(login_url='login')
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, "Access denied. Only administrators/staff can access the admin dashboard.")
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@staff_required
def admin_dashboard_view(request):
    total_users = User.objects.count()
    try:
        summary = admin_get_metrics_summary()
        all_apps = admin_list_applications()
    except Exception as e:
        messages.error(request, str(e))
        summary = {"total": 0, "applied": 0, "interviewing": 0, "offered": 0, "rejected": 0, "avg_score": 0}
        all_apps = []
        
    total_deadlines = sum(1 for app in all_apps if app.deadline)
    
    # Map user usernames to recent applications
    user_map = {u.id: u.username for u in User.objects.all()}
    recent_apps = []
    for app in all_apps[:5]:
        recent_apps.append({
            "id": app.id,
            "company_name": app.company_name,
            "job_title": app.job_title,
            "status": app.status,
            "username": user_map.get(app.user_id, "Unknown User"),
            "date_applied": app.date_applied
        })
        
    context = {
        "total_users": total_users,
        "summary": summary,
        "total_deadlines": total_deadlines,
        "all_apps": recent_apps
    }
    return render(request, 'tracker/admin_dashboard.html', context)

@staff_required
def admin_users_view(request):
    search_query = request.GET.get('search', '')
    if search_query:
        users = User.objects.filter(username__icontains=search_query) | User.objects.filter(email__icontains=search_query)
    else:
        users = User.objects.all()
        
    users_list = []
    for u in users:
        try:
            user_apps_count = get_metrics_summary(user_id=u.id)["total"]
        except Exception:
            user_apps_count = 0
        users_list.append({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "is_active": u.is_active,
            "is_staff": u.is_staff,
            "date_joined": u.date_joined,
            "total_apps": user_apps_count
        })
        
    return render(request, 'tracker/admin_users.html', {"users": users_list, "search_query": search_query})

@staff_required
def admin_toggle_user_status_view(request, user_id):
    if request.method == "POST":
        u = get_object_or_404(User, id=user_id)
        if u.is_superuser:
            messages.error(request, "Superusers status cannot be toggled.")
        else:
            u.is_active = not u.is_active
            u.save()
            messages.success(request, f"User status toggled successfully for {u.username}.")
    return redirect('admin_users')

@staff_required
def admin_applications_view(request):
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    try:
        applications = admin_list_applications(search_query=search_query, status_filter=status_filter)
    except ConnectionError as e:
        messages.error(request, str(e))
        applications = []
        
    user_map = {u.id: u.username for u in User.objects.all()}
    apps_list = []
    for app in applications:
        username = user_map.get(app.user_id, "Unknown User")
        apps_list.append({
            "id": app.id,
            "company_name": app.company_name,
            "job_title": app.job_title,
            "salary": app.salary,
            "status": app.status,
            "date_applied": app.date_applied,
            "resume_score": app.resume_score,
            "username": username
        })
        
    return render(request, 'tracker/admin_applications.html', {
        "applications": apps_list,
        "search_query": search_query,
        "status_filter": status_filter
    })
