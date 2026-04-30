from difflib import SequenceMatcher

from django.conf import settings

from .models import AIKnowledge, EscalationEvent


POSITIVE_WORDS = {"great", "thanks", "good", "happy", "awesome", "excellent"}
NEGATIVE_WORDS = {"angry", "bad", "delay", "hate", "issue", "problem", "refund", "broken"}

BASE_RESPONSES = {
    "en": "Thanks for your message. Our assistant is reviewing your request.",
    "hi": "Aapke message ke liye dhanyavaad. Hamara assistant request dekh raha hai.",
    "es": "Gracias por tu mensaje. Nuestro asistente esta revisando tu solicitud.",
}


def detect_sentiment(text):
    tokens = {t.strip(".,!?").lower() for t in text.split() if t.strip()}
    score = 0.0
    score += len(tokens & POSITIVE_WORDS) * 0.2
    score -= len(tokens & NEGATIVE_WORDS) * 0.25
    if score > 0.2:
        return score, "positive"
    if score < -0.2:
        return score, "negative"
    return score, "neutral"


def complexity_score(text):
    text_lower = text.lower()
    triggers = ["legal", "chargeback", "lawsuit", "urgent", "fraud", "cancel account"]
    trigger_hits = sum(1 for trigger in triggers if trigger in text_lower)
    size_factor = min(len(text.split()) / 40, 1.0)
    return min((trigger_hits * 0.25) + (size_factor * 0.5), 1.0)


def translated_response(language):
    return BASE_RESPONSES.get(language, BASE_RESPONSES["en"])


def get_personalized_response(ticket, text):
    language = ticket.language or "en"
    best_match = None
    best_ratio = 0.0
    for kb in AIKnowledge.objects.filter(language=language):
        ratio = SequenceMatcher(None, kb.query_pattern.lower(), text.lower()).ratio()
        if ratio > best_ratio:
            best_match = kb
            best_ratio = ratio

    if best_match and best_ratio > 0.62:
        best_match.use_count += 1
        best_match.save(update_fields=["use_count", "updated_at"])
        return best_match.answer_template, best_ratio

    return translated_response(language), best_ratio


def process_message(ticket, text):
    score = complexity_score(text)
    response, match_score = get_personalized_response(ticket, text)
    should_escalate = score >= settings.AI_COMPLEXITY_THRESHOLD and match_score < 0.7

    if should_escalate:
        EscalationEvent.objects.create(
            ticket=ticket,
            reason="High complexity message routed to human support",
            complexity_score=score,
        )
        return (
            "I have routed this issue to a human support agent for detailed assistance.",
            score,
            True,
        )

    return response, score, False


def learn_from_interaction(language, query, answer):
    AIKnowledge.objects.update_or_create(
        query_pattern=query[:255],
        language=language,
        defaults={"answer_template": answer},
    )
