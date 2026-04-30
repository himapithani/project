from django.urls import path

from .views import create_ticket, dashboard, language_switch, ticket_detail, update_ticket_status

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("tickets/new/", create_ticket, name="create_ticket"),
    path("tickets/<int:ticket_id>/", ticket_detail, name="ticket_detail"),
    path("tickets/<int:ticket_id>/status/", update_ticket_status, name="update_ticket_status"),
    path("language/", language_switch, name="language_switch"),
]
