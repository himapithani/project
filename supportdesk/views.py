from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required
from ai_assistant.services import detect_sentiment, learn_from_interaction, process_message

from .forms import MessageForm, TicketForm
from .models import Message, Ticket


@login_required
def dashboard(request):
    if request.user.role == "CUSTOMER":
        tickets = Ticket.objects.filter(customer=request.user)
    elif request.user.role == "AGENT":
        tickets = Ticket.objects.filter(assigned_agent=request.user) | Ticket.objects.filter(
            status="ESCALATED"
        )
    else:
        tickets = Ticket.objects.all()

    context = {
        "tickets": tickets.order_by("-updated_at")[:50],
        "counts": Ticket.objects.values("status").annotate(total=Count("id")),
    }
    return render(request, "supportdesk/dashboard.html", context)


@role_required("CUSTOMER", "ADMIN")
def create_ticket(request):
    form = TicketForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        ticket = form.save(commit=False)
        ticket.customer = request.user
        ticket.save()
        return redirect("ticket_detail", ticket_id=ticket.id)
    return render(request, "supportdesk/create_ticket.html", {"form": form})


@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.user.role == "CUSTOMER" and ticket.customer_id != request.user.id:
        return redirect("dashboard")
    if request.user.role == "AGENT" and (
        ticket.assigned_agent_id not in {None, request.user.id} and ticket.status != "ESCALATED"
    ):
        return redirect("dashboard")

    form = MessageForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user_message = form.save(commit=False)
        user_message.ticket = ticket
        user_message.sender = request.user
        score, label = detect_sentiment(user_message.content)
        user_message.sentiment_score = score
        user_message.sentiment_label = label
        user_message.save()

        ai_text, complexity, escalated = process_message(ticket, user_message.content)
        ai_sentiment_score, ai_label = detect_sentiment(ai_text)
        Message.objects.create(
            ticket=ticket,
            sender=request.user,
            content=ai_text,
            sentiment_score=ai_sentiment_score,
            sentiment_label=ai_label,
            is_ai_response=True,
        )
        learn_from_interaction(ticket.language, user_message.content, ai_text)

        if escalated:
            ticket.status = "ESCALATED"
        elif complexity > 0.3:
            ticket.status = "IN_PROGRESS"
        ticket.save(update_fields=["status", "updated_at"])
        return redirect("ticket_detail", ticket_id=ticket.id)

    return render(
        request,
        "supportdesk/ticket_detail.html",
        {"ticket": ticket, "messages": ticket.messages.all(), "form": form},
    )


@role_required("ADMIN", "AGENT")
def update_ticket_status(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    status = request.POST.get("status")
    if status in dict(Ticket.Status.choices):
        ticket.status = status
        ticket.assigned_agent = request.user if request.user.role == "AGENT" else ticket.assigned_agent
        ticket.save(update_fields=["status", "assigned_agent", "updated_at"])
    return redirect("ticket_detail", ticket_id=ticket.id)


@login_required
def language_switch(request):
    lang = request.GET.get("lang", "en")
    request.session["ui_lang"] = lang
    if request.user.is_authenticated:
        request.user.preferred_language = lang
        request.user.save(update_fields=["preferred_language"])
    return JsonResponse({"ok": True, "language": lang})
