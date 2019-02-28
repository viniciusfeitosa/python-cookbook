import os
from django.contrib.auth.models import User
from django.core.mail import send_mail
from newsletter.models import Newsletter
from newsletter.serializers import (
    NewsletterSerializer
)
from rest_framework import status
from rest_framework import (
    viewsets,
    permissions,
    decorators,
    response,
)


class NewsletterViewSet(viewsets.ModelViewSet):
    permission_classes = (
        permissions.IsAdminUser,
    )
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer

    @decorators.action(
        detail=True,
        methods=['get'],
        permission_classes=[permissions.IsAdminUser]
    )
    def send_newsletter(self, request, pk=None):
        try:
            mail_users = [
                u.email
                for u in User.objects.all()
            ]
            newsletter = Newsletter.objects.get(pk=pk)
            send_mail(
                newsletter.subject,
                newsletter.content,
                os.environ.get('EMAIL_USER'),
                mail_users,
                fail_silently=False
            )
        except Newsletter.DoesNotExist as ex:
            return response.Response(
                ex, status=status.HTTP_404_NOT_FOUND
            )
        return response.Response(
            'Success', status.HTTP_200_OK
        )
