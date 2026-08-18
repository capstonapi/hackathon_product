from rest_framework import serializers

from .models import Conversation, Message


class ChatRequestSerializer(serializers.Serializer):
    question = serializers.CharField(allow_blank=False)
    article_id = serializers.IntegerField(required=False)
    conversation_id = serializers.IntegerField(required=False)

    def validate(self, data):
        if not data.get("article_id") and not data.get("conversation_id"):
            raise serializers.ValidationError("Either article_id or conversation_id is required.")
        return data


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "role", "content", "citations", "sources", "trust_status", "created_at"]


class ConversationSerializer(serializers.ModelSerializer):
    article_id = serializers.IntegerField(source="article.id", read_only=True)
    article_title = serializers.CharField(source="article.title", read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ["id", "article_id", "article_title", "created_at", "updated_at", "last_message"]

    def get_last_message(self, obj):
        last = obj.messages.order_by("-created_at").first()
        return last.content if last else None
