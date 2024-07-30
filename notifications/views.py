from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from notifications.utils import send_email_notification

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Notification.objects.none()
        return Notification.objects.filter(user=self.request.user)

    @swagger_auto_schema(
        responses={
            200: openapi.Response('Успешный ответ', NotificationSerializer(many=True)),
            401: 'Неавторизован'
        },
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer <token>", type=openapi.TYPE_STRING)
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={
            200: openapi.Response('Успешный ответ', NotificationSerializer),
            401: 'Неавторизован',
            404: 'Уведомление не найдено'
        },
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer <token>", type=openapi.TYPE_STRING)
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={
            200: openapi.Response('Успешный ответ', openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING)
            })),
            401: 'Неавторизован',
            404: 'Уведомление не найдено'
        },
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer <token>", type=openapi.TYPE_STRING)
        ]
    )
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'notification marked as read'})

    @swagger_auto_schema(
        responses={
            200: openapi.Response('Успешный ответ', openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING)
            })),
            401: 'Неавторизован'
        },
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer <token>", type=openapi.TYPE_STRING)
        ]
    )
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        self.get_queryset().update(is_read=True)
        return Response({'status': 'all notifications marked as read'})

    @action(detail=False, methods=['post'])
    def send_email(self, request):
        subject = request.data.get('subject')
        message = request.data.get('message')
        if subject and message:
            send_email_notification(request.user, subject, message)
            return Response({'status': 'email sent'})
        return Response({'error': 'Subject and message are required'}, status=400)