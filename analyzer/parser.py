import re
from .services.extractor import SKILL_CATALOG

class ResumeAnalyzer:
    """
    ResumeAnalyzer OOP class representing a resume parser and keyword matcher.
    Uses Regular Expressions (re) to extract contact details and skills,
    and calculates matching compatibility percentages with Job Descriptions.
    """
    def __init__(self, resume_text):
        self.resume_text = resume_text or ""

    def extract_email(self):
        """
        Uses regular expression to extract email from the resume text.
        """
        pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        match = re.search(pattern, self.resume_text)
        return match.group(0) if match else None

    def extract_phone(self):
        """
        Uses regular expression to extract standard phone number patterns from resume text.
        Supports formats: +1-234-567-8901, (123) 456-7890, 123-456-7890, 10-digit number.
        """
        pattern = r'\b(?:\+\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}\b'
        match = re.search(pattern, self.resume_text)
        return match.group(0) if match else None

    def extract_skills(self):
        """
        Uses regular expressions (re module) to match skills from the catalog in the resume text.
        Matches are case-insensitive and enforce word boundaries.
        """
        extracted_skills = []
        for skill in SKILL_CATALOG:
            # Build regex with word boundary checking to avoid partial matches
            pattern = r'\b' + re.escape(skill).replace(r'\ ', r'[\s-]') + r'\b'
            if re.search(pattern, self.resume_text, re.IGNORECASE):
                extracted_skills.append(skill)
        return extracted_skills

    def match_to_job(self, job_description):
        """
        Matches resume skills with skills extracted from the job description.
        Calculates match percentage and identifies matched and missing keywords.
        """
        # Extract skills from job description
        job_skills = []
        for skill in SKILL_CATALOG:
            pattern = r'\b' + re.escape(skill).replace(r'\ ', r'[\s-]') + r'\b'
            if re.search(pattern, job_description, re.IGNORECASE):
                job_skills.append(skill)

        # Fallback to standard developer skills if none found in job description
        if not job_skills:
            job_skills = ["Python", "Algorithms", "OOP"]

        resume_skills = self.extract_skills()

        matched_skills = []
        missing_skills = []

        # Iterate and count matches (using loops)
        for skill in job_skills:
            match_found = False
            for r_skill in resume_skills:
                if skill.lower() == r_skill.lower():
                    match_found = True
                    break
            
            if match_found:
                matched_skills.append(skill)
            else:
                missing_skills.append(skill)

        total_required = len(job_skills)
        total_matched = len(matched_skills)
        score = int((total_matched / total_required) * 100) if total_required > 0 else 0

        return {
            "score": score,
            "matched": matched_skills,
            "missing": missing_skills,
            "total_required": total_required,
            "total_matched": total_matched,
            "email": self.extract_email(),
            "phone": self.extract_phone()
        }
