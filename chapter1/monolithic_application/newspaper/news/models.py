from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User
from django.db import models


FREE_PLAN = 'free'
SUBSCRIBER_PLAN = 'subscribers'
NEWS_PLANS = (
    ('F', FREE_PLAN),
    ('S', SUBSCRIBER_PLAN),
)


class News(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=150)
    content = models.TextField()
    plan = models.CharField(
        choices=NEWS_PLANS,
        default='free',
        max_length=len(SUBSCRIBER_PLAN)
    )
    created = models.DateTimeField(auto_now=True)
    is_ative = models.BooleanField(default=True)
    tags = ArrayField(
        models.CharField(max_length=100),
        blank=True,
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('created',)
