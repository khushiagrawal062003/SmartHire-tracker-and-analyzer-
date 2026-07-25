import pymongo
from bson.objectid import ObjectId
from django.conf import settings
from datetime import datetime
from .models import JobApplication

_db_client = None

def get_db():
    """
    Establishes or returns the existing MongoDB database connection.
    Uses MONGODB_SETTINGS from Django settings.
    """
    global _db_client
    if _db_client is None:
        mongo_cfg = settings.MONGODB_SETTINGS
        try:
            _db_client = pymongo.MongoClient(
                host=mongo_cfg['host'],
                port=mongo_cfg.get('port', 27017),
                serverSelectionTimeoutMS=5000  # Increased timeout for cloud database connection
            )
            # Force a check to verify connection
            _db_client.server_info()
        except pymongo.errors.ServerSelectionTimeoutError as e:
            raise ConnectionError(
                "Could not connect to MongoDB server. Please ensure MongoDB Community Server "
                "is installed and running locally on port 27017."
            ) from e
            
    return _db_client[settings.MONGODB_SETTINGS['db_name']]

def get_applications_collection():
    db = get_db()
    return db['applications']

def create_application(user_id, company_name, job_title, status='applied', salary='', deadline='', contact_email='', description=''):
    """
    Inserts a new job application document for a specific user into MongoDB.
    Uses the JobApplication OOP class.
    """
    collection = get_applications_collection()
    
    # Instantiate the JobApplication class
    app_obj = JobApplication(
        user_id=user_id,
        company_name=company_name,
        job_title=job_title,
        status=status,
        salary=salary,
        deadline=deadline,
        contact_email=contact_email,
        description=description
    )
    
    doc = app_obj.to_dict()
    result = collection.insert_one(doc)
    return str(result.inserted_id)

def get_application_by_id(app_id, user_id=None):
    """
    Finds a single application document by its hex string ObjectId.
    Returns a JobApplication OOP object.
    """
    collection = get_applications_collection()
    try:
        query = {"_id": ObjectId(app_id)}
        if user_id:
            query["user_id"] = user_id
            
        doc = collection.find_one(query)
        if doc:
            return JobApplication.from_dict(doc)
    except Exception:
        return None
    return None

def update_application(app_id, user_id, update_fields):
    """
    Updates specific fields in a job application document.
    """
    collection = get_applications_collection()
    try:
        query = {"_id": ObjectId(app_id), "user_id": user_id}
        result = collection.update_one(query, {"$set": update_fields})
        return result.modified_count > 0
    except Exception:
        return False

def delete_application(app_id, user_id):
    """
    Permanently deletes a job application document from MongoDB.
    """
    collection = get_applications_collection()
    try:
        query = {"_id": ObjectId(app_id), "user_id": user_id}
        result = collection.delete_one(query)
        return result.deleted_count > 0
    except Exception:
        return False

def list_applications(user_id, search_query='', status_filter=''):
    """
    Queries MongoDB for job applications owned by the user, applying
    optional searches and status filters, returning them as a list of JobApplication objects.
    Uses cursor iteration.
    """
    collection = get_applications_collection()
    
    # Base query: filter by owner
    query = {"user_id": user_id}
    
    # Apply search filter (Case-insensitive matching of company, title, or description)
    if search_query:
        query["$or"] = [
            {"company_name": {"$regex": search_query, "$options": "i"}},
            {"job_title": {"$regex": search_query, "$options": "i"}},
            {"description": {"$regex": search_query, "$options": "i"}},
        ]
        
    # Apply status filter
    if status_filter:
        query["status"] = status_filter
        
    # Query with sorting by date applied descending
    cursor = collection.find(query).sort("date_applied", pymongo.DESCENDING)
    
    apps = []
    # Cursor iteration
    for doc in cursor:
        app_obj = JobApplication.from_dict(doc)
        apps.append(app_obj)
        
    return apps

def get_metrics_summary(user_id):
    """
    Aggregates application status metrics for the specified user from MongoDB.
    """
    collection = get_applications_collection()
    
    total = collection.count_documents({"user_id": user_id})
    applied = collection.count_documents({"user_id": user_id, "status": "applied"})
    interviewing = collection.count_documents({"user_id": user_id, "status": "interviewing"})
    offered = collection.count_documents({"user_id": user_id, "status": "offered"})
    rejected = collection.count_documents({"user_id": user_id, "status": "rejected"})
    
    return {
        "total": total,
        "applied": applied,
        "interviewing": interviewing,
        "offered": offered,
        "rejected": rejected
    }

def admin_list_applications(search_query='', status_filter=''):
    """
    Queries MongoDB for all applications across all users.
    """
    collection = get_applications_collection()
    query = {}
    if search_query:
        query["$or"] = [
            {"company_name": {"$regex": search_query, "$options": "i"}},
            {"job_title": {"$regex": search_query, "$options": "i"}},
            {"description": {"$regex": search_query, "$options": "i"}},
        ]
    if status_filter:
        query["status"] = status_filter
    cursor = collection.find(query).sort("date_applied", pymongo.DESCENDING)
    apps = []
    for doc in cursor:
        apps.append(JobApplication.from_dict(doc))
    return apps

def admin_get_metrics_summary():
    """
    Aggregates application metrics across all users.
    """
    collection = get_applications_collection()
    total = collection.count_documents({})
    applied = collection.count_documents({"status": "applied"})
    interviewing = collection.count_documents({"status": "interviewing"})
    offered = collection.count_documents({"status": "offered"})
    rejected = collection.count_documents({"status": "rejected"})
    
    pipeline = [
        {"$match": {"resume_score": {"$ne": None}}},
        {"$group": {"_id": None, "avg_score": {"$avg": "$resume_score"}}}
    ]
    res = list(collection.aggregate(pipeline))
    avg_score = round(res[0]["avg_score"]) if res and len(res) > 0 and "avg_score" in res[0] and res[0]["avg_score"] is not None else 0
    
    return {
        "total": total,
        "applied": applied,
        "interviewing": interviewing,
        "offered": offered,
        "rejected": rejected,
        "avg_score": avg_score
    }
