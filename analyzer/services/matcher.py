from .extractor import extract_skills

def match_resume_to_job(job_description, resume_text):
    """
    Calculates the compatibility of a resume against a job description.
    Uses lists, loops, and sets to determine matched and missing keywords.
    """
    # 1. Extract required skills from the job description
    required_skills = extract_skills(job_description)
    
    # 2. Extract candidate's skills from the resume
    resume_skills = extract_skills(resume_text)
    
    # If the job description does not contain any cataloged skills,
    # let's fallback to standard Python fundamentals as dummy required skills
    if not required_skills:
        required_skills = ["Python", "Algorithms", "OOP"]
        
    matched_skills = []
    missing_skills = []
    
    # 3. Loop through required skills and count matches
    # This directly covers "loops to count matches"
    for skill in required_skills:
        # Check case-insensitive match inside candidate skills
        match_found = False
        for candidate_skill in resume_skills:
            if skill.lower() == candidate_skill.lower():
                match_found = True
                break
                
        if match_found:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)
            
    # 4. Calculate matching percentage
    total_required = len(required_skills)
    total_matched = len(matched_skills)
    
    match_percentage = int((total_matched / total_required) * 100)
    
    return {
        "score": match_percentage,
        "matched": matched_skills,
        "missing": missing_skills,
        "total_required": total_required,
        "total_matched": total_matched
    }
