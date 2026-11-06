# AgentX

AgentX is a Streamlit chat app powered by Groq. The Streamlit UI imports the
backend's database and LLM functions directly, so the app runs as one service
and does not require a separate FastAPI deployment.

## Run locally

1. Install the dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

2. Set `GROQ_API_KEY` in a local `.env` file (see `.env.example`).
3. Start the app from the repository root:

   ```powershell
   streamlit run frontend/app.py
   ```

## Deploy to Streamlit Community Cloud

1. Push this repository to GitHub.
2. In [Streamlit Community Cloud](https://share.streamlit.io/), create an app
   from the repository and select `frontend/app.py` as the **Main file path**.
3. In the app's **Settings → Secrets**, add:

   ```toml
   GROQ_API_KEY = "your-groq-api-key"
   ```

   Optionally set `GROQ_MODEL` in the same file to override the default model.
4. Deploy. Streamlit Cloud installs `requirements.txt` and runs the Streamlit
   entry point; no FastAPI server or separate frontend deployment is needed.

Conversation data is stored in `storage/agentx.db`. Streamlit Community Cloud's
local filesystem is not durable, so conversations may be lost when the app is
restarted or redeployed. Use an external database if conversation history must
persist reliably across deployments.
