from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
import json

from django.http import StreamingHttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .serializers import ChatRequestSerializer, ConversationSerializer, MessageSerializer


class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = services.ask_question(
            request.user,
            serializer.validated_data["question"],
            article_id=serializer.validated_data.get("article_id"),
            conversation_id=serializer.validated_data.get("conversation_id"),
        )
        return Response(result)


class ChatStreamView(APIView):
    """SSE transport emits product-safe stages and a final structured result.
    It intentionally never streams prompts, tool calls, or chain-of-thought.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        def events():
            for status in ("Searching internal knowledge...", "Retrieving evidence...", "Verifying evidence...", "Generating answer..."):
                yield f"event: status\ndata: {json.dumps({'status': status})}\n\n"
            result = services.ask_question(request.user, serializer.validated_data["question"], article_id=serializer.validated_data.get("article_id"), conversation_id=serializer.validated_data.get("conversation_id"))
            # Retrieval timestamps can be datetime objects.  SSE bypasses
            # DRF's JSON renderer, so serialize them explicitly here.
            yield f"event: answer\ndata: {json.dumps(result, default=str)}\n\n"

        response = StreamingHttpResponse(events(), content_type="text/event-stream")
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response


class ConversationMessagesView(ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return services.get_conversation_messages(self.request.user, self.kwargs["conversation_id"])


class HistoryView(ListAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return services.list_conversations(self.request.user)
