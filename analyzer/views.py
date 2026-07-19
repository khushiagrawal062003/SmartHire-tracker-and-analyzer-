from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from tracker.db import get_application_by_id, update_application, list_applications
from analyzer.parser import ResumeAnalyzer

@login_required(login_url='login')
def upload_resume_view(request):
    """
    Renders the upload page, passing the list of user's job applications.
    """
    user_id = request.user.id
    try:
        applications = list_applications(user_id=user_id)
    except ConnectionError as e:
        messages.error(request, str(e))
        applications = []
        
    selected_app_id = request.GET.get('app_id', '')
    
    return render(request, 'analyzer/upload_resume.html', {
        "applications": applications,
        "selected_app_id": selected_app_id
    })

@login_required(login_url='login')
def analyze_resume_view(request):
    """
    Handles file upload, reads the text content, executes Regex matching,
    calculates match percentage, saves results to MongoDB, and displays report.
    """
    if request.method == "POST":
        app_id = request.POST.get('app_id')
        resume_file = request.FILES.get('resume')
        
        if not app_id or not resume_file:
            messages.error(request, "Please select a job application and upload a resume file.")
            return redirect('upload_resume')
            
        # File type validation
        if not resume_file.name.endswith('.txt'):
            messages.error(request, "Only plain text (.txt) files are supported for parsing.")
            return redirect('upload_resume')
            
        try:
            # 1. Fetch application details from MongoDB
            app = get_application_by_id(app_id, user_id=request.user.id)
            if not app:
                messages.error(request, "Target job application not found.")
                return redirect('upload_resume')
                
            # 2. File handling: read resume content (handles exceptions)
            try:
                resume_text = resume_file.read().decode('utf-8', errors='replace')
            except Exception as fe:
                raise IOError(f"Could not read uploaded file: {fe}")
                
            # 3. Match resume skills to job description keywords
            job_description = app.get('description', '')
            analysis = ResumeAnalyzer(resume_text).match_to_job(job_description)
            
            # 4. Save analysis results back to the MongoDB document
            update_data = {
                "resume_score": analysis['score'],
                "matched_keywords": analysis['matched'],
                "missing_keywords": analysis['missing']
            }
            update_application(app_id, user_id=request.user.id, update_fields=update_data)
            
            # Refresh app document with new database state
            app.update(update_data)
            
            context = {
                "app": app,
                "score": analysis['score'],
                "matched": analysis['matched'],
                "missing": analysis['missing']
            }
            messages.success(request, f"Resume parsed and matched successfully against {app['company_name']}!")
            return render(request, 'analyzer/analysis_result.html', context)
            
        except ConnectionError as ce:
            messages.error(request, str(ce))
        except Exception as e:
            messages.error(request, f"Analysis failed: {e}")
            
    return redirect('upload_resume')
