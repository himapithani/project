from django import forms

from .models import Message, Ticket


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["subject", "language"]


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Describe your issue or ask a question..."}
            )
        }
