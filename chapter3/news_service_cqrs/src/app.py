import json
import logging
import mongoengine
import uuid

from nameko.events import (
    event_handler,
    EventDispatcher
)
from nameko.rpc import (
    rpc,
    RpcProxy,
)
from nameko.web.handlers import http
from nameko_sqlalchemy import DatabaseSession

from .models.news import (
    Base,
    NewsCommandModel,
    NewsQueryModel,
)
from .schemas.news import NewsSchema


class NewsServiceAPI:
    name = 'news_service_api'
    query_stack = RpcProxy('query_stack')
    command_stack = RpcProxy('command_stack')

    @http('POST', '/create_news')
    def create_news(self, request):
        schema = NewsSchema(strict=True)
        try:
            data = schema.loads(request.get_data(as_text=True)).data
        except ValueError:
            return 400, 'Invalid payload'

        try:
            news_id = self.command_stack.news_domain(data)
            localtion = {
                'Location': 'http://localhost:5001/news/{}'.format(news_id)
            }
            return 202, localtion, 'ACCEPTED'
        except Exception as e:
            logging.error(e)
            return 500, 'Internal Server Error'

    @http('GET', '/news/list/page/<int:page>/limit/<int:limit>')
    def list_news(self, request, page, limit):
        respose_data = self.query_stack.list_news(page, limit)
        return 200, {'Content-Type': 'application/json'}, respose_data

    @http('GET', '/news/<string:news_id>')
    def get_news(self, request, news_id):
        respose_data = self.query_stack.get_news(news_id)
        return 200, {'Content-Type': 'application/json'}, respose_data


class CommandNewsService:
    name = 'command_stack'
    dispatcher = EventDispatcher()
    db = DatabaseSession(Base)

    @rpc
    def news_domain(self, data):
        try:
            data['id'] = str(uuid.uuid1())
            news = NewsCommandModel(data)
            self.db.add(news)
            self.db.commit()
            self.dispatcher('news_created', data)
            return data.get('id')
        except Exception as e:
            self.db.rollback()
            logging.error(e)


class EventsComponet:
    name = 'events_component'

    @event_handler('command_stack', 'news_created')
    def news_created_normalize_db(self, data):
        try:
            NewsQueryModel(**data).save()
        except Exception as e:
            logging.error(e)


class QueryNewsService:
    name = 'query_stack'

    @rpc
    def list_news(self, page, limit):
        try:
            if not page:
                page = 1
            offset = (page - 1) * limit
            news_list = NewsQueryModel.objects.skip(offset).limit(limit)
            return news_list.to_json()
        except Exception as e:
            logging.error(e)
            return json.dumps({'error': str(e)})

    @rpc
    def get_news(self, news_id):
        try:
            news = NewsQueryModel.objects.get(id=news_id)
            return news.to_json()
        except mongoengine.DoesNotExist as e:
            logging.error(e)
            return json.dumps({'error': str(e)})
        except Exception as e:
            logging.error(e)
            return json.dumps({'error': str(e)})
