import json

from nameko.web.handlers import http
from nameko_sqlalchemy import DatabaseSession

from .models.news import (
    Base,
    NewsModel,
)
from .schema.news import NewsSchema


class NewsService:
    name = 'news_service'

    db = DatabaseSession(Base)

    @http('POST', '/news')
    def create_news(self, request):
        schema = NewsSchema(strict=True)
        try:
            data = schema.loads(request.get_data(as_text=True)).data
        except ValueError as error:
            return Exception(error)

        news = NewsModel(data)

        self.db.add(news)
        self.db.commit()
        respose_data = schema.dump(news).data
        return 201, json.dumps(respose_data)

    @http('GET', '/news')
    def list_news(self, request):
        news = self.db.query(NewsModel).all()
        respose_data = NewsSchema().dump(news, many=True).data
        return 200, json.dumps(respose_data)

    @http('GET', '/news/<int:news_id>')
    def get_news(self, request, news_id):
        news = self.db.query(NewsModel).get(news_id)
        if not news:
            return Exception('error: news not found')

        respose_data = NewsSchema().dump(news).data
        return 200, json.dumps(respose_data)

    @http('PUT', '/news/<int:news_id>')
    def udpate_news(self, request, news_id):
        schema = NewsSchema(strict=True)
        try:
            data = schema.loads(
                request.get_data(as_text=True),
                partial=True,
            ).data
        except ValueError as error:
            return Exception(error)

        news = self.db.query(NewsModel).get(news_id)
        news.author = data.get('author')
        news.title = data.get('title')
        news.content = data.get('content')
        news.is_active = data.get('is_active')
        news.tags = data.get('tags')
        self.db.commit()
        respose_data = NewsSchema().dump(news).data
        return 200, json.dumps(respose_data)

    @http('DELETE', '/news/<int:news_id>')
    def delete_news(self, request, news_id):
        news = self.db.query(NewsModel).get(news_id)
        self.db.delete(news)
        self.db.commit()
        return 204, 'News ID {} Deleted'.format(news_id)
