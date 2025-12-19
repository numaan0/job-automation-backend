# app/services/skill_matcher_service.py

from langchain_google_vertexai import ChatVertexAI
from langchain.agents import create_agent
from app.schemas.job import SkillMatchResult
from typing import List
from app.services.llm_service import get_llm_groq


# Your constant skills
YOUR_SKILLS = [
    "python", "django", "flask", "fastapi","react"
    "postgresql", "sqlite", "aws", "docker",
    "react", "javascript", "git", "rest api", "angular js", "github", "ec2","typescript"
]


class SkillMatcherService:
    """
    Match job descriptions against your skills using LLM
    Returns structured Pydantic output
    """
    
    def __init__(self):
        
        llm = get_llm_groq()
        
        # Create agent with structured output
        self.agent = create_agent(
            model=llm,
            response_format=SkillMatchResult  # Pydantic model
        )
    
    async def match_job(self, job_description: str) -> SkillMatchResult:
        """
        Match job against your skills
        
        Returns Pydantic model: SkillMatchResult
        """
        
        result = self.agent.invoke({
            "messages": [{
                "role": "user",
                "content": f"""My skills: {', '.join(YOUR_SKILLS)}

            Job description:
            {job_description[:3000]}

            Analyze which of MY skills are mentioned in this job.
            Calculate match score as percentage of my skills that match.
            Return matched skills, missing skills, and score."""
                        }]
                    })
        
        # Returns SkillMatchResult Pydantic model
        return result["structured_response"]
