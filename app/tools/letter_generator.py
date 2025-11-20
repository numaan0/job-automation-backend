from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.services.llm_service import get_llm

@tool
def generate_cover_letter(job_title: str, company: str, matched_skills: str) -> str:
    """Generate a tailored cover letter based on job details and matched skills"""
    llm = get_llm()
    
    template = PromptTemplate.from_template(
        """Write a professional, concise cover letter for the {job_title} position at {company}.
        Highlight these skills: {matched_skills}
        
        Keep it under 300 words, professional tone, compelling but not overly creative."""
    )
    
    chain = template | llm | StrOutputParser()
    return chain.invoke({
        "job_title": job_title,
        "company": company,
        "matched_skills": matched_skills
    })
