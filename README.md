# AgentX

AgentX is a conversational AI assistant built with Streamlit and powered by
Groq's chat-completions API. It supports streaming responses and keeps a local
SQLite history of conversations.

The recommended deployment runs the complete app as **one Streamlit
application**. The Streamlit UI imports the database and Groq service directly;
it does not need to make HTTP requests to a separately deployed backend.

## Features

- Chat with a Groq-hosted language model and display its response as it streams.
- Start a new conversation and switch between saved conversations.
- Automatically title conversations from the first user message.
- Delete a conversation and its messages from the sidebar.
- Keep conversation history in a SQLite database.
- Use suggested prompts from the welcome screen.

## How it works

```text
Browser
  ↕ Streamlit
frontend/app.py
  ├── backend/llm_service.py ── Groq API
  └── backend/database.py ───── storage/agentx.db (SQLite)
```

When a user submits a prompt, the Streamlit app loads the conversation history,
sends that context to Groq, displays the generated response as a stream, and
saves the user and assistant messages to SQLite. There is no separate backend
service in this flow.

`backend/main.py` contains a FastAPI API implementation, but it is not started
or used by the Streamlit app. It is not required for local Streamlit use or the
single-app Streamlit Cloud deployment described here.

## Requirements

- Python 3
- A [Groq API key](https://console.groq.com/keys)
- Internet access for the app to call Groq

## Run locally

Run commands from the repository root.

### 1. Create and activate a virtual environment

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Configure the Groq API key

Copy `.env.example` to `.env` and replace the placeholder values:

```dotenv
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
```

`GROQ_MODEL` is optional; if omitted, AgentX uses
`llama-3.3-70b-versatile`. Choose a model that is available to your Groq
account. Keep `.env` private and do not commit API keys.

### 4. Start Streamlit

```bash
python -m streamlit run frontend/app.py
```

Streamlit prints a local URL in the terminal (usually
`http://localhost:8501`). Stop the app with `Ctrl+C`.

## Deploy to Streamlit Community Cloud

### Before deploying

1. Push the project to a GitHub repository that Streamlit Community Cloud can
   access.
2. Confirm that `requirements.txt` is in the repository root and that the
   Streamlit entry point is `frontend/app.py`.
3. Do not commit `.env` or any API key. Streamlit Cloud secrets are used for
   production configuration.

### Create the app

1. Open [Streamlit Community Cloud](https://share.streamlit.io/) and sign in.
2. Choose **Create app**, then select the GitHub repository and branch.
3. Set **Main file path** to:

   ```text
   frontend/app.py
   ```

4. Create the app and open **App settings → Secrets**.
5. Add the following TOML secret, replacing the value with your key:

   ```toml
   GROQ_API_KEY = "your-groq-api-key"
   ```

   To select a different supported Groq model, optionally add:

   ```toml
   GROQ_MODEL = "llama-3.3-70b-versatile"
   ```

6. Save the settings and deploy (or reboot the app if it is already deployed).

Streamlit Cloud installs the packages listed in `requirements.txt` and runs the
Streamlit entry point. You do not need to deploy FastAPI, configure an API URL,
or run a second service.

## Configuration

| Name | Required | Default | Description |
| --- | --- | --- | --- |
| `GROQ_API_KEY` | Yes | None | Groq API key used to authenticate requests. Set it in `.env` for local use or Streamlit secrets for Cloud. |
| `GROQ_MODEL` | No | `llama-3.3-70b-versatile` | Groq model ID used for chat completion. Must be available to your Groq account. |

For local development, values can be loaded from `.env`. On Streamlit Cloud,
add them in the app's Secrets settings. Environment variables take precedence
over Streamlit secrets when both are set.

## Conversation storage and privacy

The app initializes a SQLite database at `storage/agentx.db`. It creates the
database directory and required tables when Streamlit starts. Conversations
are stored in that database, not in the browser session.

**Streamlit Community Cloud's local filesystem is not durable.** Conversation
history may disappear when the app restarts, is redeployed, or its environment
is replaced. SQLite on the app's local filesystem is suitable for local
development and lightweight demonstrations, but it is not durable,
multi-instance storage. Use a managed external database if conversation
history must persist reliably.

The current app does not implement user accounts or per-user conversation
access controls. Conversations in the shared database are visible in the
sidebar to visitors using the same deployed app, and the UI allows them to
delete conversations. Do not use this deployment for private or sensitive
conversations without adding authentication and access controls.

## Repository layout

```text
.
├── backend/
│   ├── database.py       # SQLite setup and conversation/message operations
│   ├── llm_service.py    # Groq client, model selection, and response streaming
│   └── main.py           # Optional FastAPI API; not used by the Streamlit app
├── frontend/
│   └── app.py            # Streamlit UI and application entry point
├── storage/
│   └── agentx.db         # SQLite conversation database
├── test/
│   └── test_llm.py       # Manual live-Groq response check
├── .env.example          # Local environment variable template
├── requirements.txt      # Python dependencies for the Streamlit app
└── README.md
```

## Testing

There is a small manual Groq integration check:

```bash
python test/test_llm.py
```

It sends a request to Groq, so it requires a valid `GROQ_API_KEY`, network
access, and an available model. It is not an offline unit test.

To check that the application starts locally, run:

```bash
python -m streamlit run frontend/app.py
```

Then open the local URL printed by Streamlit and send a prompt.

## Troubleshooting

### Missing API key

If AgentX reports that `GROQ_API_KEY` is not configured, check that:

- Locally, `.env` is in the repository root and contains a valid key.
- On Streamlit Cloud, the key is saved under **App settings → Secrets** using
  valid TOML syntax.
- The app has been rebooted after changing its secrets.

### Model or Groq request errors

Confirm that the configured model ID is available to your Groq account and
that your account can make requests. Check the Streamlit app logs for the
underlying Groq error.

### Conversation history is missing

The app uses a local SQLite file. On Streamlit Cloud, local files can be
replaced during restarts or redeployments. Use external persistent storage if
the app requires durable history.
