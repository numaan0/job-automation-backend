from langchain_google_vertexai import ChatVertexAI
from langchain_groq import ChatGroq
from app.core.config import get_settings
from google.cloud.aiplatform_v1beta1.types import Tool, GoogleSearchRetrieval

settings = get_settings()

def get_llm(enable_grounding:bool =False)->ChatVertexAI:
    """
    Initialize and return Vertex AI LLM instance
    
    Args:
        enable_grounding: Enable Google Search grounding for real-time data
    """
    llm_params={
        "model_name": settings.MODEL_NAME,
        "temperature": settings.MODEL_TEMPERATURE,
        "project": settings.GOOGLE_CLOUD_PROJECT,
        "location": settings.GOOGLE_CLOUD_REGION
    }
    if enable_grounding:
        search_retrieval = GoogleSearchRetrieval(
            dynamic_retrieval_config={
                "mode": "MODE_DYNAMIC",
                "dynamic_threshold": 0.7
            }
        )
        # searchRetrievalTool = {
        #     "googleSearchRetrieval":{
        #         "dynamicRetrievalConfig":{
        #             "mode": "MODE_DYNAMIC",
        #             "dynamicThreshold":0.7
        #             }
        #     }
        # }
        # tool = Tool(google_search_retrieval=search_retrieval)
        tool = Tool(google_search={})

        return ChatVertexAI(**llm_params).bind_tools([tool])
        
    else:    
        return ChatVertexAI(**llm_params)



def get_llm_groq():
    """
    Return Groq-hosted Llama model for LangChain.
    No grounding needed.
    """
    return ChatGroq(
        groq_api_key=settings.GROQ_API_KEY,
        model_name="llama-3.1-8b-instant",
        temperature=settings.MODEL_TEMPERATURE
    )    