from langchain_core.tools import tool

@tool
def search_resume(required_skills: str) -> str:
    """Search resume for skills matching the required skills list"""
    # Placeholder - in production, you'd parse actual resume
    resume_skills = ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS", "React"]
    matched = [skill for skill in resume_skills if skill.lower() in required_skills.lower()]
    return f"Found in resume: {', '.join(matched) if matched else 'No matches found'}"
