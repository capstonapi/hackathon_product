from django.urls import path

from .views import ChatStreamView, ChatView, ConversationMessagesView

urlpatterns = [
    path("", ChatView.as_view(), name="chat"),
    path("stream/", ChatStreamView.as_view(), name="chat-stream"),
    path("<int:conversation_id>/", ConversationMessagesView.as_view(), name="chat-detail"),
]
