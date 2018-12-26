from news.models import News
from news.serializers import (
    NewsSerializer
)

from rest_framework import (
    viewsets,
    permissions,
)


class NewsViewSet(viewsets.ModelViewSet):
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )
    queryset = News.objects.all()
    serializer_class = NewsSerializer
