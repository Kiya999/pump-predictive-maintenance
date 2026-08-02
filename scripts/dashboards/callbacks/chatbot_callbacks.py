# chatbot_callbacks.py
import os
import glob
import requests
from dash import callback, Input, Output, State, html

from dashboard_config import (
    CHATBOT_DOCS_DIR,
    OLLAMA_HOST,
    CHATBOT_MAX_CHARS_PER_FILE,
    CHATBOT_REQUEST_TIMEOUT_S,
)


def _load_docs_context():
    """
    Reads all .md files in CHATBOT_DOCS_DIR fresh on every question. if the performance is frustrating, we need to implement caching 
    """
    if not os.path.isdir(CHATBOT_DOCS_DIR):
        return None, f"Docs folder not found: {CHATBOT_DOCS_DIR}"

    md_files = sorted(glob.glob(os.path.join(CHATBOT_DOCS_DIR, "*.md")))
    if not md_files:
        return None, f"No .md files found in {CHATBOT_DOCS_DIR}"

    sections = []
    for path in md_files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()[:CHATBOT_MAX_CHARS_PER_FILE]
            sections.append(f"--- {os.path.basename(path)} ---\n{content}")
        except Exception as e:
            sections.append(f"--- {os.path.basename(path)} (unreadable: {e}) ---")

    return "\n\n".join(sections), None


def _query_ollama(question, context, model):
    prompt = (
        "You are answering questions about a pump/motor fleet using only "
        "the reference documents below. If the documents do not contain "
        "the answer, say so explicitly instead of guessing.\n\n"
        f"REFERENCE DOCUMENTS:\n{context}\n\n"
        f"QUESTION: {question}\n\nANSWER:"
    )
    try:
        resp = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=CHATBOT_REQUEST_TIMEOUT_S,
        )
        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            return None, f"Ollama error: {data['error']}"
        return data.get("response", "").strip(), None
    except requests.exceptions.ConnectionError:
        return None, (
            f"Could not reach Ollama at {OLLAMA_HOST}. "
            f"Is it running? Start it with `ollama serve`."
        )
    except requests.exceptions.Timeout:
        return None, (
            f"Ollama request timed out after {CHATBOT_REQUEST_TIMEOUT_S}s. "
            f"The 8B models (qwen3) are noticeably slower on CPU "
            f"— consider raising CHATBOT_REQUEST_TIMEOUT_S or switching model."
        )
    except Exception as e:
        return None, f"Ollama request failed: {e}"


def _render_history(history):
    bubbles = []
    for turn in history:
        bubbles.append(html.Div([
            html.Div(
                f"Q ({turn.get('model', '?')}): {turn['question']}",
                style={"fontWeight": "bold", "marginBottom": 4}
            ),
            html.Div(turn["answer"], style={"color": "#2c3e50", "whiteSpace": "pre-wrap"}),
        ], style={
            "marginBottom": 10,
            "paddingBottom": 8,
            "borderBottom": "1px solid #ecf0f1",
        }))
    return bubbles


@callback(
    Output("chatbot-history-store", "data"),
    Output("chatbot-history-display", "children"),
    Output("chatbot-input", "value"),
    Input("chatbot-submit-btn", "n_clicks"),
    State("chatbot-input", "value"),
    State("chatbot-model-selector", "value"),
    State("chatbot-history-store", "data"),
    prevent_initial_call=True,
)
def handle_chatbot_question(n_clicks, question, selected_model, history):
    history = history or []

    if not question or not question.strip():
        return history, _render_history(history), ""

    context, doc_error = _load_docs_context()
    if doc_error:
        history = history + [{"question": question, "model": selected_model, "answer": f"[Error] {doc_error}"}]
        return history, _render_history(history), ""

    answer, err = _query_ollama(question.strip(), context, selected_model)
    if err:
        history = history + [{"question": question, "model": selected_model, "answer": f"[Error] {err}"}]
    else:
        history = history + [{"question": question, "model": selected_model, "answer": answer}]

    return history, _render_history(history), ""
