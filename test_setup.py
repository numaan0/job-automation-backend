import os
from dotenv import load_dotenv
from langchain_google_vertexai import ChatVertexAI

load_dotenv()

try:
    print("Testing Vertex AI setup...")
    
    # Test LLM initialization
    llm = ChatVertexAI(
        model_name="gemini-2.0-flash-exp",
        project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("GOOGLE_CLOUD_REGION")
    )
    
    print("✅ LLM initialized successfully")
    
    # Test simple invocation
    response = llm.invoke("What is 2+2?")
    print(f"✅ LLM response: {response.content}")
    
    print("\n✅ Vertex AI setup is working!")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    print("\nTroubleshooting:")
    print("1. Check .env file has correct paths")
    print("2. Check GOOGLE_APPLICATION_CREDENTIALS points to JSON file")
    print("3. Check JSON file exists in that location")
    print("4. Check Vertex AI API is enabled")
