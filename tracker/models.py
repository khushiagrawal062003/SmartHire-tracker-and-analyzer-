from datetime import datetime
from bson.objectid import ObjectId
import pymongo
from django.conf import settings

class JobApplication:
    """
    JobApplication OOP class representing a job application document.
    Handles data fields, dictionary serialization/deserialization for MongoDB.
    Supports dict-like access for Django views.
    """
    def __init__(self, user_id, company_name, job_title, status='applied', 
                 salary='', date_applied=None, deadline='', contact_email='', 
                 description='', resume_score=None, matched_keywords=None, 
                 missing_keywords=None, _id=None):
        self.id = str(_id) if _id else None
        self.user_id = user_id
        self.company_name = company_name
        self.job_title = job_title
        self.status = status
        self.salary = salary
        self.date_applied = date_applied or datetime.today().strftime('%Y-%m-%d')
        self.deadline = deadline
        self.contact_email = contact_email
        self.description = description
        self.resume_score = resume_score
        self.matched_keywords = matched_keywords or []
        self.missing_keywords = missing_keywords or []

    def to_dict(self):
        """
        Serializes the JobApplication object to a dictionary for MongoDB storage.
        """
        doc = {
            "user_id": self.user_id,
            "company_name": self.company_name,
            "job_title": self.job_title,
            "status": self.status,
            "salary": self.salary,
            "date_applied": self.date_applied,
            "deadline": self.deadline,
            "contact_email": self.contact_email,
            "description": self.description,
            "resume_score": self.resume_score,
            "matched_keywords": self.matched_keywords,
            "missing_keywords": self.missing_keywords
        }
        if self.id:
            doc["_id"] = ObjectId(self.id)
        return doc

    @classmethod
    def from_dict(cls, doc):
        """
        Creates a JobApplication instance from a MongoDB document.
        """
        if not doc:
            return None
        
        # Extract fields
        _id = doc.get('_id')
        user_id = doc.get('user_id')
        company_name = doc.get('company_name')
        job_title = doc.get('job_title')
        status = doc.get('status', 'applied')
        salary = doc.get('salary', '')
        date_applied = doc.get('date_applied')
        deadline = doc.get('deadline', '')
        contact_email = doc.get('contact_email', '')
        description = doc.get('description', '')
        resume_score = doc.get('resume_score')
        matched_keywords = doc.get('matched_keywords', [])
        missing_keywords = doc.get('missing_keywords', [])

        return cls(
            user_id=user_id,
            company_name=company_name,
            job_title=job_title,
            status=status,
            salary=salary,
            date_applied=date_applied,
            deadline=deadline,
            contact_email=contact_email,
            description=description,
            resume_score=resume_score,
            matched_keywords=matched_keywords,
            missing_keywords=missing_keywords,
            _id=_id
        )

    def __getitem__(self, key):
        """
        Allows dictionary-like access to object attributes.
        """
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"JobApplication has no attribute {key}")

    def get(self, key, default=None):
        """
        Allows dictionary-like get access to object attributes.
        """
        return getattr(self, key, default)

    def update(self, fields_dict):
        """
        Updates fields on the object from a dictionary.
        """
        for k, v in fields_dict.items():
            if hasattr(self, k):
                setattr(self, k, v)
