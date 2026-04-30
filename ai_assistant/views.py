from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from supportdesk.models import Ticket

from .services import detect_sentiment, process_message


@login_required
@require_POST
def realtime_query(request):
    ticket_id = request.POST.get("ticket_id")
    text = request.POST.get("text", "")
    ticket = Ticket.objects.filter(id=ticket_id).first()
    if not ticket:
        return JsonResponse({"error": "Ticket not found"}, status=404)

    response, complexity, escalated = process_message(ticket, text)
    score, label = detect_sentiment(response)
    return JsonResponse(
        {
            "response": response,
            "complexity": complexity,
            "escalated": escalated,
            "sentiment": {"score": score, "label": label},
        }
    )
