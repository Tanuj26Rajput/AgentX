
import os

from groq import Groq
from dotenv import load_dotenv
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError


# ==========================================
# 1. ENVIRONMENT CONFIGURATION
# ==========================================

load_dotenv()

DEFAULT_MODEL = "llama-3.3-70b-versatile"


def get_client():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        try:
            api_key = st.secrets["GROQ_API_KEY"]
        except (KeyError, StreamlitSecretNotFoundError) as error:
            raise RuntimeError(
                "Configure GROQ_API_KEY in the environment or Streamlit secrets."
            ) from error

    return Groq(api_key=api_key)


def get_model():
    model = os.getenv("GROQ_MODEL")

    if model:
        return model

    try:
        return st.secrets.get("GROQ_MODEL", DEFAULT_MODEL)
    except StreamlitSecretNotFoundError:
        return DEFAULT_MODEL


# ==========================================
# 2. NORMAL CHAT RESPONSE
# ==========================================

def generate_response(messages):
    """
    Generate an AI response using Groq.

    Args:
        messages: List of conversation messages.

    Returns:
        Generated assistant response.
    """

    try:

        completion = get_client().chat.completions.create(
            model=get_model(),
            messages=messages,
            temperature=0.7,
            max_completion_tokens=1024
        )

        return completion.choices[0].message.content

    except Exception as e:

        print(f"Groq API Error: {e}")

        return "Sorry, something went wrong. Please try again."


# ==========================================
# 3. STREAMING CHAT RESPONSE
# ==========================================

def stream_response(messages):
    """
    Generate an AI response as a stream of text chunks.
    """

    try:

        stream = get_client().chat.completions.create(
            model=get_model(),
            messages=messages,
            temperature=0.7,
            max_completion_tokens=1024,
            stream=True
        )

        for chunk in stream:

            if chunk.choices:

                content = chunk.choices[0].delta.content

                if content:
                    yield content

    except Exception as e:

        print(f"Groq Streaming Error: {e}")

        raise
