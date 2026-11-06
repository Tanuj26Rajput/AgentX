
import os
import uuid
import streamlit as st

from datetime import datetime

from backend.database import (
    delete_conversation,
    get_all_conversations,
    get_conversation,
    get_conversation_messages,
    initialize_database,
    save_message,
)
from backend.llm_service import stream_response


# ==========================================
# 1. CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="AgentX - AI Assistant",
    page_icon="🤖",
    layout="wide"
)

initialize_database()


# ==========================================
# 2. CUSTOM CSS
# ==========================================

def load_css():

    css_path = os.path.join(
        os.path.dirname(__file__),
        "static",
        "styles.css"
    )

    if os.path.exists(css_path):

        with open(css_path, "r", encoding="utf-8") as file:

            st.markdown(
                f"<style>{file.read()}</style>",
                unsafe_allow_html=True
            )


load_css()


# ==========================================
# 3. SESSION STATE INITIALIZATION
# ==========================================

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "delete_target" not in st.session_state:
    st.session_state.delete_target = None

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None


# ==========================================
# 4. DATA HELPERS
# ==========================================

def fetch_conversations():
    return get_all_conversations()


def load_conversation(thread_id):

    if not get_conversation(thread_id):
        st.error("Unable to load conversation: conversation not found.")
        return False

    messages = get_conversation_messages(thread_id)
    st.session_state.thread_id = thread_id
    st.session_state.messages = [
        {
            "role": msg["role"],
            "content": msg["content"]
        }
        for msg in messages
    ]

    return True


def remove_conversation(thread_id):

    if not delete_conversation(thread_id):
        st.error("Unable to delete conversation: conversation not found.")
        return

    if st.session_state.thread_id == thread_id:
        st.session_state.thread_id = None
        st.session_state.messages = []

    st.session_state.delete_target = None
    st.toast("Conversation deleted successfully!")
    st.rerun()


def format_timestamp(timestamp):

    try:

        date = datetime.fromisoformat(timestamp)

        return date.astimezone().strftime(
            "%d %b %Y, %I:%M %p"
        )

    except (ValueError, TypeError):

        return ""


# ==========================================
# 5. SIDEBAR
# ==========================================

with st.sidebar:

    st.title("🤖 AgentX")

    st.caption("Your Intelligent AI Assistant")

    st.divider()

    # New Chat button
    if st.button(
        "＋ New Chat",
        use_container_width=True,
        type="primary"
    ):

        st.session_state.thread_id = None
        st.session_state.messages = []
        st.session_state.delete_target = None

        st.rerun()

    st.divider()

    st.subheader("Recent Conversations")

    conversations = fetch_conversations()

    if not conversations:

        st.caption("Your conversations will appear here.")

    else:

        for conversation in conversations:

            thread_id = conversation["id"]
            title = conversation["title"]

            is_active = (
                st.session_state.thread_id == thread_id
            )

            col1, col2 = st.columns([5, 1])

            with col1:

                if st.button(
                    f"{'● ' if is_active else '💬 '}{title}",
                    key=f"chat_{thread_id}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary"
                ):

                    if load_conversation(thread_id):
                        st.rerun()

            with col2:

                if st.button(
                    "🗑️",
                    key=f"delete_{thread_id}",
                    help="Delete conversation"
                ):

                    if st.session_state.delete_target == thread_id:
                        st.session_state.delete_target = None
                    else:
                        st.session_state.delete_target = thread_id

                    st.rerun()

            # Display timestamp
            timestamp = format_timestamp(
                conversation["updated_at"]
            )

            if timestamp:
                st.caption(timestamp)

    # Delete confirmation
    delete_target = st.session_state.delete_target

    if delete_target:

        st.divider()

        st.warning("Delete this conversation permanently?")

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "Delete",
                type="primary",
                use_container_width=True
            ):

                remove_conversation(delete_target)

        with col2:

            if st.button(
                "Cancel",
                use_container_width=True
            ):

                st.session_state.delete_target = None
                st.rerun()

    st.divider()

    st.caption("Powered by Groq + Llama")


# ==========================================
# 6. MAIN INTERFACE
# ==========================================

if not st.session_state.messages:

    # Welcome screen
    st.title("🤖 AgentX")

    st.markdown(
        "### Your intelligent AI assistant."
    )

    st.caption(
        "Ask questions, explore ideas, and get things done."
    )

    st.divider()

    st.subheader("What can I help you with?")

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "🧠 Explain AI Agents",
            use_container_width=True
        ):

            st.session_state.pending_prompt = (
                "Explain AI agents with practical examples."
            )

            st.rerun()

        if st.button(
            "🐍 Python Programming",
            use_container_width=True
        ):

            st.session_state.pending_prompt = (
                "Teach me an interesting Python concept."
            )

            st.rerun()

    with col2:

        if st.button(
            "🔍 Explain RAG",
            use_container_width=True
        ):

            st.session_state.pending_prompt = (
                "Explain Retrieval-Augmented Generation."
            )

            st.rerun()

        if st.button(
            "⚡ AI Project Ideas",
            use_container_width=True
        ):

            st.session_state.pending_prompt = (
                "Suggest interesting AI engineering projects."
            )

            st.rerun()

else:

    st.title("AgentX")

    st.caption("Your conversation")


# ==========================================
# 7. DISPLAY CONVERSATION HISTORY
# ==========================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# ==========================================
# 8. CHAT INPUT
# ==========================================

prompt = st.chat_input(
    "Message AgentX..."
)

if not prompt:

    prompt = st.session_state.pending_prompt

    st.session_state.pending_prompt = None


# ==========================================
# 9. PROCESS USER MESSAGE
# ==========================================

if prompt:

    # Create a conversation if one doesn't exist
    if st.session_state.thread_id is None:

        st.session_state.thread_id = str(uuid.uuid4())

    thread_id = st.session_state.thread_id

    # Save user message in frontend state
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    history = get_conversation_messages(thread_id)
    messages = [
        {
            "role": "system",
            "content": (
                "You are AgentX, a helpful AI assistant. "
                "Answer clearly, accurately, and conversationally."
            )
        },
        *[
            {
                "role": message["role"],
                "content": message["content"]
            }
            for message in history
        ],
        {
            "role": "user",
            "content": prompt
        }
    ]

    save_message(thread_id, "user", prompt)

    with st.chat_message("user"):

        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):

        try:

            with st.spinner("AgentX is thinking..."):
                ai_response = st.write_stream(stream_response(messages))

            save_message(thread_id, "assistant", ai_response)
            st.session_state.messages.append({
                "role": "assistant",
                "content": ai_response
            })

        except Exception as e:

            st.error(f"AgentX could not generate a response: {e}")

    # Refresh sidebar and conversation
    st.rerun()
