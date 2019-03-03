from nameko.rpc import rpc
from nameko_sqlalchemy import DatabaseSession

from ..models.news import (
    Base,
    NewsModel,
)
from ..schema.news import NewsSchema


class NewsRepositoryService:
    name = 'news_repository'

    db = DatabaseSession(Base)

    @rpc
    def create_news(self, request):
        data, error = NewsSchema().load(request)
        if error:
            return Exception(error)

        news = NewsModel(data)

        self.db.add(news)
        self.db.commit()
        return NewsSchema().dump(news).data

    @rpc
    def list_news(self):
        news = self.db.query(NewsModel).all()
        return NewsSchema().dump(news, many=True).data

    @rpc
    def get_news(self, news_id):
        news = self.db.query(NewsModel).get(news_id)
        if not news:
            return Exception('error: news not found')

        return NewsSchema().dump(news).data

    @rpc
    def update_news(self, request):
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
        return NewsSchema().dump(news).data

    @rpc
    def delete_news(self, news_id):
        news = self.db.query(NewsModel).get(news_id)
        self.db.delete(news)
        return {'message': 'News {} deleted'.format(news_id)}
