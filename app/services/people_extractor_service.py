from langchain.agents import create_agent
from app.schemas.hiring_manager import PeopleExtractionResponse
from app.services.llm_service import get_llm_groq


class LLMPeopleExtractor:
    """
    Extracts hiring managers, engineering managers, technical leads, etc.
    from webpage text using Groq LLM with structured output.
    """

    def __init__(self):
        llm = get_llm_groq()

        # Create a structured-output agent
        self.agent = create_agent(
            model=llm,
            response_format=PeopleExtractionResponse  # Pydantic schema
        )

    async def extract_people(self, text: str) -> PeopleExtractionResponse:
        """
        Extract relevant people using structured LLM output.
        """

        prompt = f"""
Extract ALL relevant people from the following text.

ONLY include individuals whose job role includes ANY of these:
- engineering manager
- hiring manager
- tech lead
- software lead
- staff engineer
- senior developer
- senior software engineer
- recruiter
- talent acquisition
- development manager
- delivery manager

Return STRICT structured JSON according to schema.

TEXT:
{text[:6000]}
"""

        try:
            result = self.agent.invoke({
                "messages": [{
                    "role": "user",
                    "content": prompt
                }]
            })

            return result["structured_response"]

        except Exception as e:
            print(f"❌ People extraction failed: {e}")
            return PeopleExtractionResponse(people=[])
