# chatbot_callbacks.py
import os
import glob
import json
import uuid
import requests
from dash import callback, Input, Output, State, html, ctx, ALL
from dash.exceptions import PreventUpdate

from dashboard_config import (
    CHATBOT_DOCS_DIR,
    OLLAMA_HOST,
    CHATBOT_MAX_CHARS_PER_FILE,
    CHATBOT_REQUEST_TIMEOUT_S,
)


def _load_docs_context():
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


def _query_ollama(question, context, model, history=None, selected_asset=None, start_date=None, end_date=None):
    history = history or []

    context_prefix = ""
    if selected_asset and end_date:
        context_prefix = (
            f"Current dashboard view: Asset {selected_asset}, viewing data through {start_date}-{end_date}. "
            f"Keep answers focused on this asset and timeframe when relevant.\n\n"
        )

    conversation_history = ""
    if history:
        conversation_history = "PRIOR CONVERSATION:\n"
        for turn in history:
            conversation_history += f"Q: {turn['question']}\nA: {turn['answer']}\n\n"

    prompt = (
        "You are answering questions about a pump/motor fleet using only "
        "the reference documents below. If the documents do not contain "
        "the answer, say so explicitly instead of guessing.\n\n"
        f"{context_prefix}"
        f"REFERENCE DOCUMENTS:\n{context}\n\n"
        f"{conversation_history}"
        f"QUESTION: {question}\n\nANSWER:"
    )

    try:
        resp = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={"model": model, "prompt": prompt, "stream": True},
            timeout=CHATBOT_REQUEST_TIMEOUT_S,
            stream=True,
        )
        resp.raise_for_status()

        full_response = ""
        for line in resp.iter_lines():
            if line:
                try:
                    chunk = json.loads(line)
                    if "response" in chunk:
                        full_response += chunk["response"]
                except json.JSONDecodeError:
                    pass

        return full_response.strip(), None

    except requests.exceptions.ConnectionError:
        return None, (
            f"Could not reach Ollama at {OLLAMA_HOST}. "
            f"Is it running? Start it with `ollama serve`."
        )
    except requests.exceptions.Timeout:
        return None, (
            f"Ollama timed out after {CHATBOT_REQUEST_TIMEOUT_S}s. "
            f"Try a smaller model or increase CHATBOT_REQUEST_TIMEOUT_S."
        )
    except Exception as e:
        return None, f"Ollama request failed: {e}"


def _render_history(history):
    bubbles = []
    for turn in history:
        bubbles.append(html.Div([
            html.Div(
                f"Q: {turn['question']}",
                style={"fontWeight": "bold", "marginBottom": 4, "fontSize": 11, "color": "#2980b9"}
            ),
            html.Div(turn["answer"], style={"color": "#2c3e50", "whiteSpace": "pre-wrap", "fontSize": 11}),
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
    Output("chatbot-send-button", "disabled"),
    Output("chatbot-send-button", "children"),
    Output("chatbot-pending-trigger", "data"),
    Input({"type": "suggested-question", "index": ALL}, "n_clicks"),
    Input("chatbot-send-button", "n_clicks"),
    State({"type": "suggested-question", "index": ALL}, "children"),
    State("chatbot-input", "value"),
    State("chatbot-model-selector", "value"),
    State("chatbot-history-store", "data"),
    State("asset-selector", "value"),
    State("date-range-picker", "start_date"),
    State("date-range-picker", "end_date"),
    prevent_initial_call=True,
)
def handle_chatbot_input(suggested_clicks, send_clicks, suggested_texts, textarea_value, selected_model,
                         history, selected_asset, start_date, end_date):
    history = history or []
    question_clean = ""

    # Suggested question clicked
    if isinstance(ctx.triggered_id, dict) and ctx.triggered_id.get("type") == "suggested-question":
        idx = ctx.triggered_id.get("index")
        if suggested_texts and idx < len(suggested_texts):
            question_clean = suggested_texts[idx]

    elif ctx.triggered_id == "chatbot-send-button":
        question_clean = textarea_value.strip() if textarea_value else ""

    # don't process empty questions
    if not question_clean:
        raise PreventUpdate

    turn_id = str(uuid.uuid4())
    pending_history = history + [{
        "id": turn_id,
        "question": question_clean,
        "model": selected_model,
        "answer": "⏳ Generating response..."
    }]

    trigger_data = {
        "turn_id": turn_id,
        "question": question_clean,
        "model": selected_model,
        "history": history,
        "selected_asset": selected_asset,
        "start_date": start_date,
        "end_date": end_date,
    }

    return pending_history, _render_history(pending_history), "", True, "Thinking...", trigger_data


@callback(
    Output("chatbot-history-store", "data", allow_duplicate=True),
    Output("chatbot-history-display", "children", allow_duplicate=True),
    Output("chatbot-send-button", "disabled", allow_duplicate=True),
    Output("chatbot-send-button", "children", allow_duplicate=True),
    Input("chatbot-pending-trigger", "data"),
    State("chatbot-history-store", "data"),
    prevent_initial_call=True,
    background=True,
)
def fetch_ollama_response(trigger_data, history):
    if not trigger_data:
        raise PreventUpdate

    history = history or []
    turn_id = trigger_data["turn_id"]
    question_clean = trigger_data["question"]
    selected_model = trigger_data["model"]
    prior_history = trigger_data["history"]
    selected_asset = trigger_data["selected_asset"]
    start_date = trigger_data["start_date"]
    end_date = trigger_data["end_date"]

    def _write_answer(text):
        target = next((h for h in history if h.get("id") == turn_id), None)
        if target is not None:
            target["answer"] = text

    context, doc_error = _load_docs_context()
    if doc_error:
        _write_answer(f"[Error] {doc_error}")
        return history, _render_history(history), False, "Send"

    answer, err = _query_ollama(
        question_clean,
        context,
        selected_model,
        history=prior_history,
        selected_asset=selected_asset,
        start_date=start_date,
        end_date=end_date
    )

    _write_answer(answer if not err else f"[Error] {err}")

    return history, _render_history(history), False, "Send"
