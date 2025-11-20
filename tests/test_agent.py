# # test_agent_tools.py
# import json
# from langchain.agents import create_agent
# from langchain_core.tools import tool
# from app.services.llm_service import get_llm

# # 1) simple tool that logs & returns a predictable JSON string
# @tool
# def ping_tool(query: str) -> str:
#     """simple tool that logs & returns a predictable JSON string"""
#     print("PING_TOOL_CALLED with:", query)
#     return json.dumps({"pong": query.upper()})

# # 2) create a minimal model instance (use your get_llm() if available)
# # If you have a Chat model wrapper already, use it; else use a simple model id:
# # model = "openai:gpt-4o"  # or your get_llm()
# # model = "gpt-4o-mini"  # replace with your configured model identifier or pass instance
# llm=get_llm()
# agent = create_agent({
#     llm,
#     tools= [ping_tool],
#     "systemPrompt": "You are an agent. When asked to ping, call ping_tool and only emit tool output."
# })

# # 3) invoke the agent with an explicit instruction to call the tool
# resp = agent.invoke({
#     "messages": [{"role": "user", "content": "Please call ping_tool with query 'hello' and return only its output."}]
# })

# print("AGENT RESPONSE:", resp)
# # Look for evidence:
# # - Printed "PING_TOOL_CALLED..."
# # - resp should include either tool output or tool call metadata
