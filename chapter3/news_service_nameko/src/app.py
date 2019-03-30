import json
import logging
import mongoengine
import os
import uuid

from nameko.events import (
    event_handler,
    EventDispatcher
)
from nameko.rpc import (
    rpc,
    RpcProxy,
)
from nameko.standalone.rpc import ClusterRpcProxy
from nameko.web.handlers import http
from nameko_sqlalchemy import DatabaseSession

from .models.news import (
    Base,
    NewsCommandModel,
    NewsQueryModel,
)
from .schemas.news import NewsSchema

CONFIG = {'AMQP_URI': os.environ.get('QUEUE_HOST')}


class NewsServiceAPI:
    name = 'news_service_api'
    news_rpc = RpcProxy('query_stack')

    @http('POST', '/create_news')
    def create_news(self, request):
        schema = NewsSchema(strict=True)
        try:
            data = schema.loads(request.get_data(as_text=True)).data
        except ValueError:
            return 400, 'Invalid payload'

        try:
            with ClusterRpcProxy(CONFIG) as cluster_rpc:
                data.id = str(uuid.uuid1())
                cluster_rpc.command_stack.news_domain(data)
            localtion = {
                'Location': 'http://localhost:5001/news/{}'.format(data['id'])
            }
            return 202, localtion, 'ACCEPTED'
        except Exception:
            return 500, 'Internal Server Error'

    @http('GET', '/news/list/page/<int:page>/limit/<int:limit>')
    def list_news(self, request, page, limit):
        news_list = self.news_rpc.list_news(page, limit)
        respose_data = NewsSchema().dump(news_list, many=True).data
        return 200, json.dumps(respose_data)

    @http('GET', '/news/<string:news_id>')
    def get_news(self, request, news_id):
        news = self.news_rpc.get_news(news_id)
        respose_data = NewsSchema().dump(news).data
        return 200, json.dumps(respose_data)


class CommandNewsService:
    name = 'command_stack'
    dispatcher = EventDispatcher()
    db = DatabaseSession(Base)

    @rpc
    def create_news(self, data):
        try:
            news = NewsCommandModel(data)
            self.db.add(news)
            self.db.commit()
            self.dispatcher('news_created', data)
        except Exception as e:
            self.db.rollback()
            logging.error(e)


class EventsComponet:
    name = 'events_component'

    @event_handler('command_stack', 'news_created')
    def news_created_normalize_db(self, data):
        try:
            news = NewsQueryModel(data)
            news.save()
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
            return json.dumps({'error': e})

    @rpc
    def get_news(self, news_id):
        try:
            news = NewsQueryModel.objects.get(id=id)
            return news.to_json()
        except mongoengine.DoesNotExist as e:
            return json.dumps({'error': e})
        except Exception as e:
            return json.dumps({'error': e})
