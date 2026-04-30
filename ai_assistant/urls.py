from django.urls import path

from .views import realtime_query

urlpatterns = [
    path("realtime-query/", realtime_query, name="realtime_query"),
]
