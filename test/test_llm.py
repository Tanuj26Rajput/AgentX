from backend.llm_service import generate_response

messages = [
    {
        "role": "system",
        "content": "You are AgentX, a helpful AI assistant."
    },
    {
        "role": "user",
        "content": "Explain why fast inference is important."
    }
]

response = generate_response(messages)
print("AgentX:", response)