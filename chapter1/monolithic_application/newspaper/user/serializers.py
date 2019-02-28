from django.contrib.auth.models import User, Group
from news.models import News
from rest_framework import serializers


# Serializers define the API representation.
class UserSerializer(serializers.ModelSerializer):
    my_news = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'url',
            'username',
            'email',
            'my_news',
            'is_staff',
            'is_active',
            'groups'
        )

    def get_my_news(self, obj):
        print(type(obj))
        print(type(obj.__dict__))
        # if obj.groups.objects.filter(name='author'):
        if any([
            True
            for g in obj.groups.all()
            if g.name == 'author'
        ]):
            return News.objects.filter(author=obj)


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')
