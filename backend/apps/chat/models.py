from django.conf import settings
from django.db import models

from apps.articles.models import Article


class Conversation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="conversations")
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]


class Message(models.Model):
    ROLE_CHOICES = [("user", "user"), ("assistant", "assistant")]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=16, choices=ROLE_CHOICES)
    content = models.TextField()
    citations = models.JSONField(default=list, blank=True)
    sources = models.JSONField(default=list, blank=True)
    trust_status = models.CharField(max_length=32, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
