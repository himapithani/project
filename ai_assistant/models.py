from django.db import models
from supportdesk.models import Ticket


class AIKnowledge(models.Model):
    query_pattern = models.CharField(max_length=255, unique=True)
    answer_template = models.TextField()
    language = models.CharField(max_length=10, default="en")
    use_count = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.query_pattern


class EscalationEvent(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="escalations")
    reason = models.CharField(max_length=255)
    complexity_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
