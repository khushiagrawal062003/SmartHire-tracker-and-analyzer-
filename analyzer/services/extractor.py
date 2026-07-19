import re

# Standard catalog of common developer/HR-Tech skills
SKILL_CATALOG = [
    # Programming Languages
    "Python", "JavaScript", "Java", "C++", "C#", "Ruby", "Go", "Rust", "Swift", "PHP", "TypeScript", "SQL",
    
    # Web Frameworks
    "Django", "Flask", "FastAPI", "React", "Angular", "Vue", "Spring", "Express", "Laravel",
    
    # Databases
    "MongoDB", "PostgreSQL", "MySQL", "SQLite", "Redis", "Cassandra", "NoSQL",
    
    # APIs & Formats
    "RESTful", "REST API", "GraphQL", "JSON", "XML", "DRF", "Django REST Framework",
    
    # Tools, Cloud & DevOps
    "Git", "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Linux", "CI/CD",
    
    # Core Concepts
    "Regex", "Regular Expressions", "Threading", "Multithreading", "OOP", "Object Oriented Programming",
    "Data Structures", "Algorithms", "Machine Learning", "Data Analysis", "HTML", "CSS", "Bootstrap"
]

def extract_skills(text):
    """
    Uses Python's regular expressions (re module) to match skills from the catalog
    in the provided text. Matches are case-insensitive and enforce word boundaries.
    """
    if not text:
        return []
        
    extracted_skills = []
    
    for skill in SKILL_CATALOG:
        # Build regex with word boundary checking to avoid partial matches (e.g. "Go" inside "Google")
        # Support optional hyphens and spaces (e.g., "REST API" and "REST-API")
        pattern = r'\b' + re.escape(skill).replace(r'\ ', r'[\s-]') + r'\b'
        
        if re.search(pattern, text, re.IGNORECASE):
            extracted_skills.append(skill)
            
    return extracted_skills
