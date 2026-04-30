from django.db.models import Avg, Count
from django.shortcuts import render

from accounts.decorators import role_required
from ai_assistant.models import EscalationEvent
from supportdesk.models import Message, Ticket


@role_required("ADMIN")
def analytics_dashboard(request):
    ticket_stats = Ticket.objects.values("status").annotate(total=Count("id")).order_by("status")
    sentiment_stats = (
        Message.objects.values("sentiment_label").annotate(avg=Avg("sentiment_score"), total=Count("id"))
    )
    escalation_count = EscalationEvent.objects.count()
    context = {
        "ticket_stats": ticket_stats,
        "sentiment_stats": sentiment_stats,
        "escalation_count": escalation_count,
        "total_tickets": Ticket.objects.count(),
    }
    return render(request, "insights/analytics.html", context)
