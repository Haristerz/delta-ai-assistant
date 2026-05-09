import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI
from backend.config import settings
from ai_engine.intent_classifier import classify_intent
from ai_engine.rag_pipeline import retrieve
from ai_engine.prompt_builder import build_prompt

client = OpenAI(
    api_key=settings.openai_api_key,
    base_url=settings.openai_base_url,
)

INTENTS_NEEDING_RAG = {"miles_policy", "baggage", "upgrade"}

ALLOWED_INTENTS = {"miles_policy", "baggage", "upgrade", "account"}

GUARDRAIL_REPLY = (
    "I'm Delta's AI Customer Assistant. I can only help with questions about "
    "your miles balance, baggage policies, flight upgrades, or your account. "
    "Please ask me something related to your Delta travel experience."
)

def get_ai_response(user_message: str, customer: dict) -> dict:
    intent   = classify_intent(user_message)
    used_rag = False
    rag_context = ""

    if intent not in ALLOWED_INTENTS:
        return {"reply": GUARDRAIL_REPLY, "intent": intent, "used_rag": False}

    if intent in INTENTS_NEEDING_RAG:
        rag_context = retrieve(user_message, intent)
        used_rag    = True

    messages = build_prompt(
        user_message=user_message,
        intent=intent,
        customer_context=customer,
        rag_context=rag_context,
    )

    response = client.chat.completions.create(
        model=settings.model_name,
        messages=messages,
        max_tokens=512,
        temperature=0.7,
    )

    reply = response.choices[0].message.content.strip()

    return {
        "reply":    reply,
        "intent":   intent,
        "used_rag": used_rag,
    }
