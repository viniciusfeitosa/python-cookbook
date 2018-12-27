from newsletter.models import Newsletter
from rest_framework import serializers


class NewsletterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Newsletter
        fields = '__all__'
