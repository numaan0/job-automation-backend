from app.services.llm_service import get_llm
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.tools import tool



@tool
def extract_job_skills(job_description: str) -> str:
    """Extract skills from job posting"""
    llm = get_llm()  # ← Creates instance using Vertex AI config
    
    template = PromptTemplate.from_template(
        "Extract skills: {job_description}"
    )
    chain = template | llm | StrOutputParser()
    return chain.invoke({"job_description": job_description})
