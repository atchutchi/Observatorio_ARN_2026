from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import ChatSession, ChatMessage
from .serializers import (
    ChatSessionSerializer, ChatSessionDetailSerializer,
    ChatMessageSerializer, QuerySerializer,
)
from .services import GeminiAssistant


class AssistantQueryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = QuerySerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        user_message = ser.validated_data['message']
        session_id = ser.validated_data.get('session_id')

        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id, user=request.user)
            except ChatSession.DoesNotExist:
                session = ChatSession.objects.create(user=request.user, title=user_message[:100])
        else:
            session = ChatSession.objects.create(user=request.user, title=user_message[:100])

        ChatMessage.objects.create(
            session=session, role='user', content=user_message,
        )

        chat_history = list(
            session.messages.order_by('created_at').values('role', 'content'),
        )

        assistant = GeminiAssistant()
        response_text = assistant.query(user_message, chat_history=chat_history[:-1])

        assistant_msg = ChatMessage.objects.create(
            session=session, role='assistant', content=response_text,
        )

        if not session.title or session.title == user_message[:100]:
            session.title = user_message[:100]
            session.save(update_fields=['title'])

        return Response({
            'session_id': session.id,
            'message': ChatMessageSerializer(assistant_msg).data,
        })


class ChatSessionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ChatSessionDetailSerializer
        return ChatSessionSerializer
