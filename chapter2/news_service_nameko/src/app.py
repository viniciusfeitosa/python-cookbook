import json

from nameko.rpc import RpcProxy
from nameko.web.handlers import http


class NewsViewService:
    name = 'news_view'

    repository = RpcProxy('news_repository')

    @http('POST', '/')
    def create_news(self, request):
        news = self.repository.create_news(request)
        return 201, json.dumps(news)

    @http('GET', '/')
    def list_news(self, request):
        news = self.repository.list_news()
        return 200, json.dumps(news)

    @http('GET', '/<int:news_id>')
    def get_news(self, request, news_id):
        news = self.repository.get_news(news_id)
        return 200, json.dumps(news)

    @http('PUT', '/')
    def udpate_news(self, request):
        news = self.repository.update_news(request)
        return 200, json.dumps(news)

    @http('DELETE', '/<int:news_id>')
    def delete_news(self, news_id):
        news = self.repository.update_news(news_id)
        return 204, json.dumps(news)
