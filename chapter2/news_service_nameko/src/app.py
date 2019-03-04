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

    @http('POST', '/')
    def create_news(self, request):
        data, error = NewsSchema().load(request)
        if error:
            return Exception(error)

        news = NewsModel(data)

        self.db.add(news)
        self.db.commit()
        respose_data = NewsSchema().dump(news).data
        return 201, json.dumps(respose_data)

    @http('GET', '/')
    def list_news(self, request):
        news = self.db.query(NewsModel).all()
        respose_data = NewsSchema().dump(news, many=True).data
        return 200, json.dumps(respose_data)

    @http('GET', '/<int:news_id>')
    def get_news(self, request, news_id):
        news = self.db.query(NewsModel).get(news_id)
        if not news:
            return Exception('error: news not found')

        respose_data = NewsSchema().dump(news).data
        return 200, json.dumps(respose_data)

    @http('PUT', '/')
    def udpate_news(self, request):
        data, error = NewsSchema().load(request, partial=True)
        if error:
            return Exception(error)

        news = self.db.query(NewsModel).get(request['id'])
        news.author = request.get('author')
        news.title = request.get('title')
        news.content = request.get('content')
        news.is_active = request.get('is_active')
        news.tags = request.get('tags')
        self.db.commit()
        respose_data = NewsSchema().dump(news).data
        return 200, json.dumps(respose_data)

    @http('DELETE', '/<int:news_id>')
    def delete_news(self, news_id):
        news = self.db.query(NewsModel).get(news_id)
        self.db.delete(news)
        respose_data = {'message': 'News {} deleted'.format(news_id)}
        return 204, json.dumps(respose_data)
