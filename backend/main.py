from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from uuid import UUID

from backend.llm_service import (
    generate_response,
    stream_response
)

from backend.database import (
    initialize_database,
    save_message,
    get_all_conversations,
    get_conversation,
    get_conversation_messages,
    delete_conversation
)


# ==========================================
# 1. INITIALIZE FASTAPI APPLICATION
# ==========================================

app = FastAPI(
    title="AgentX API",
    description="Backend API for AgentX AI Assistant",
    version="1.0.0"
)


# ==========================================
# 2. DATABASE INITIALIZATION
# ==========================================

@app.on_event("startup")
def startup_event():
    initialize_database()


# ==========================================
# 3. VALIDATE CONVERSATION ID
# ==========================================

def validate_thread_id(thread_id: str):

    try:
        UUID(thread_id)

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid conversation ID"
        )


# ==========================================
# 4. PREPARE CONVERSATION MESSAGES
# ==========================================

def prepare_messages(thread_id: str, new_message: str):

    history = get_conversation_messages(thread_id)

    messages = [
        {
            "role": "system",
            "content": (
                "You are AgentX, a helpful AI assistant. "
                "Answer clearly, accurately, and conversationally."
            )
        }
    ]

    # Include previous messages
    messages.extend([
        {
            "role": msg["role"],
            "content": msg["content"]
        }
        for msg in history
    ])

    # Include latest user message
    messages.append({
        "role": "user",
        "content": new_message
    })

    return messages


# ==========================================
# 5. REQUEST MODELS
# ==========================================

class ChatRequest(BaseModel):
    thread_id: str
    message: str


class ChatResponse(BaseModel):
    thread_id: str
    response: str


# ==========================================
# 6. HEALTH CHECK
# ==========================================

@app.get("/health")
def health_check():

    return {
        "status": "AgentX API is running"
    }


# ==========================================
# 7. CONVERSATION MANAGEMENT
# ==========================================

@app.get("/api/conversations")
def list_conversations():

    return {
        "conversations": get_all_conversations()
    }


@app.get("/api/conversations/{thread_id}")
def load_conversation(thread_id: str):

    validate_thread_id(thread_id)

    conversation = get_conversation(thread_id)

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    messages = get_conversation_messages(thread_id)

    return {
        "conversation": conversation,
        "messages": messages
    }


@app.delete("/api/conversations/{thread_id}")
def remove_conversation(thread_id: str):

    validate_thread_id(thread_id)

    deleted = delete_conversation(thread_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    return {
        "message": "Conversation deleted successfully"
    }


# ==========================================
# 8. NORMAL CHAT ENDPOINT
# ==========================================

@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    validate_thread_id(request.thread_id)

    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )

    try:

        messages = prepare_messages(
            request.thread_id,
            request.message
        )

        # Save user message
        save_message(
            request.thread_id,
            "user",
            request.message
        )

        ai_response = generate_response(messages)

        # Save assistant response
        save_message(
            request.thread_id,
            "assistant",
            ai_response
        )

        return ChatResponse(
            thread_id=request.thread_id,
            response=ai_response
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Error generating response: {str(e)}"
        )


# ==========================================
# 9. STREAMING CHAT ENDPOINT
# ==========================================

@app.post("/api/chat/stream")
def chat_stream(request: ChatRequest):

    validate_thread_id(request.thread_id)

    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )

    try:

        messages = prepare_messages(
            request.thread_id,
            request.message
        )

        # Save user message before generation
        save_message(
            request.thread_id,
            "user",
            request.message
        )

        def generate_and_save():

            full_response = ""

            try:

                for chunk in stream_response(messages):

                    full_response += chunk

                    yield chunk

                # Save completed assistant response
                if full_response:
                    save_message(
                        request.thread_id,
                        "assistant",
                        full_response
                    )

            except Exception as e:

                print(f"Streaming error: {e}")

                yield "\n[AGENTX_ERROR] Response generation failed."

        return StreamingResponse(
            generate_and_save(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no"
            }
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Error starting stream: {str(e)}"
        )
