from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from analyzer.parser import ResumeAnalyzer

from tracker.db import (
    list_applications,
    create_application,
    get_application_by_id,
    update_application,
    delete_application
)
from .serializers import ApplicationSerializer

class ApplicationListCreateAPIView(APIView):
    # Enforce standard session/token authentication
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Retrieves all job applications for the authenticated user from MongoDB.
        """
        try:
            applications = list_applications(user_id=request.user.id)
            serializer = ApplicationSerializer(applications, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ConnectionError as ce:
            return Response({"error": str(ce)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
    def post(self, request):
        """
        Creates a new application document in MongoDB.
        """
        serializer = ApplicationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                company_name = serializer.validated_data['company_name']
                job_title = serializer.validated_data['job_title']
                status_val = serializer.validated_data.get('status', 'applied')
                salary = serializer.validated_data.get('salary', '')
                deadline = serializer.validated_data.get('deadline', '')
                contact_email = serializer.validated_data.get('contact_email', '')
                description = serializer.validated_data.get('description', '')
                
                # Insert directly to MongoDB
                inserted_id = create_application(
                    user_id=request.user.id,
                    company_name=company_name,
                    job_title=job_title,
                    status=status_val,
                    salary=salary,
                    deadline=deadline,
                    contact_email=contact_email,
                    description=description
                )
                
                # Retrieve the newly created document
                new_app = get_application_by_id(inserted_id, user_id=request.user.id)
                response_serializer = ApplicationSerializer(new_app)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except ConnectionError as ce:
                return Response({"error": str(ce)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ApplicationDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, app_id):
        """
        Returns a single application document by its ID.
        """
        try:
            app = get_application_by_id(app_id, user_id=request.user.id)
            if not app:
                return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
            serializer = ApplicationSerializer(app)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ConnectionError as ce:
            return Response({"error": str(ce)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
    def put(self, request, app_id):
        """
        Updates an application document.
        """
        try:
            app = get_application_by_id(app_id, user_id=request.user.id)
            if not app:
                return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        except ConnectionError as ce:
            return Response({"error": str(ce)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
        serializer = ApplicationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                update_fields = {
                    "company_name": serializer.validated_data['company_name'],
                    "job_title": serializer.validated_data['job_title'],
                    "status": serializer.validated_data.get('status', 'applied'),
                    "salary": serializer.validated_data.get('salary', ''),
                    "deadline": serializer.validated_data.get('deadline', ''),
                    "contact_email": serializer.validated_data.get('contact_email', ''),
                    "description": serializer.validated_data.get('description', '')
                }
                
                update_application(app_id, user_id=request.user.id, update_fields=update_fields)
                
                # Fetch updated document
                updated_app = get_application_by_id(app_id, user_id=request.user.id)
                response_serializer = ApplicationSerializer(updated_app)
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, app_id):
        """
        Deletes an application document from MongoDB.
        """
        try:
            success = delete_application(app_id, user_id=request.user.id)
            if not success:
                return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
            return Response({"message": "Application deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except ConnectionError as ce:
            return Response({"error": str(ce)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ResumeAnalyzeAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request, app_id):
        """
        DRF API to upload and analyze a resume file (.txt) against a specific job application.
        """
        resume_file = request.FILES.get('resume')
        if not resume_file:
            return Response({"error": "No resume file uploaded."}, status=status.HTTP_400_BAD_REQUEST)
            
        if not resume_file.name.endswith('.txt'):
            return Response({"error": "Only plain text (.txt) files are supported."}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # 1. Fetch application details
            app = get_application_by_id(app_id, user_id=request.user.id)
            if not app:
                return Response({"detail": "Job application not found."}, status=status.HTTP_404_NOT_FOUND)
                
            # 2. Read resume text
            try:
                resume_text = resume_file.read().decode('utf-8', errors='replace')
            except Exception as fe:
                return Response({"error": f"Could not read uploaded file: {fe}"}, status=status.HTTP_400_BAD_REQUEST)
                
            # 3. Analyze using ResumeAnalyzer class
            analyzer_instance = ResumeAnalyzer(resume_text)
            analysis = analyzer_instance.match_to_job(app.get('description', ''))
            
            # 4. Save to MongoDB
            update_data = {
                "resume_score": analysis['score'],
                "matched_keywords": analysis['matched'],
                "missing_keywords": analysis['missing']
            }
            update_application(app_id, user_id=request.user.id, update_fields=update_data)
            
            # Return response
            return Response({
                "message": "Resume matched and analyzed successfully.",
                "company_name": app.get('company_name'),
                "job_title": app.get('job_title'),
                "resume_score": analysis['score'],
                "matched_keywords": analysis['matched'],
                "missing_keywords": analysis['missing'],
                "extracted_email": analysis['email'],
                "extracted_phone": analysis['phone']
            }, status=status.HTTP_200_OK)
            
        except ConnectionError as ce:
            return Response({"error": str(ce)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
