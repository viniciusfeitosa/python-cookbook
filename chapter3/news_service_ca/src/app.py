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
from nameko_redis import Redis

from .models.news import (
    Base,
    NewsCommandModel,
    NewsQueryModel,
)
from .schemas.news import NewsSchema

CACHE_ALL = 'cache_all'


class NewsServiceAPI:
    name = 'news_service_api'
    query_stack = RpcProxy('query_stack')
    command_stack = RpcProxy('command_stack')

    @http('POST', '/news')
    def create_news(self, request):
        schema = NewsSchema(strict=True)
        try:
            data = schema.loads(request.get_data(as_text=True)).data
        except ValueError:
            return 400, 'Invalid payload'

        try:
            news_id = self.command_stack.create_news(data)
            localtion = {
                'Location': 'http://localhost:5001/news/{}'.format(news_id)
            }
            return 202, localtion, 'ACCEPTED'
        except Exception as e:
            logging.error(e)
            return 500, 'Internal Server Error'

    @http('PUT', '/news/<string:news_id>')
    def update_news(self, request, news_id):
        schema = NewsSchema(strict=True)
        try:
            data = schema.loads(request.get_data(as_text=True)).data
        except ValueError:
            return 400, 'Invalid payload'

        try:
            data['id'] = news_id
            news_id = self.command_stack.edit_news(data)
            localtion = {
                'Location': 'http://localhost:5001/news/{}'.format(news_id)
            }
            return 202, localtion, 'ACCEPTED'
        except Exception as e:
            logging.error(e)
            return 500, 'Internal Server Error'

    @http('PUT', '/news/<string:news_id>/publish')
    def publish_news(self, request, news_id):
        try:
            news_id = self.command_stack.publish_news(news_id)
            localtion = {
                'Location': 'http://localhost:5001/news/{}'.format(news_id)
            }
            return 202, localtion, 'ACCEPTED'
        except Exception as e:
            logging.error(e)
            return 500, 'Internal Server Error'

    @http('PUT', '/news/<string:news_id>/unpublish')
    def unpublish_news(self, request, news_id):
        try:
            news_id = self.command_stack.unpublish_news(news_id)
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
    def create_news(self, data):
        try:
            data['id'] = str(uuid.uuid1())
            data['version'] = 1
            data['status'] = 'CREATED'
            news = NewsCommandModel(data)
            self.db.add(news)
            self.db.commit()
            self.dispatcher('news_created', data)
            return data.get('id')
        except Exception as e:
            self.db.rollback()
            logging.error(e)

    @rpc
    def edit_news(self, data):
        try:
            news = self.db.query(NewsCommandModel).filter(
                NewsCommandModel.id == data.get('id')
            ).order_by(NewsCommandModel.version.desc())[0]
            data['version'] = news.version + 1
            data['status'] = 'UPDATED'
            news = NewsCommandModel(data)
            self.db.add(news)
            self.db.commit()
            self.dispatcher('news_edited', data)
            return data.get('id')
        except Exception as e:
            self.db.rollback()
            logging.error(e)

    @rpc
    def publish_news(self, news_id):
        try:
            news = self.db.query(NewsCommandModel).filter(
                NewsCommandModel.id == news_id
            ).order_by(NewsCommandModel.version.desc())[0]
            data = NewsSchema().dump(news).data
            data['version'] = news.version + 1
            data['status'] = 'PUBLISHED'
            data['is_active'] = True
            news_data = NewsCommandModel(data)
            self.db.add(news_data)
            self.db.commit()
            self.dispatcher('news_edited', data)
            return data.get('id')
        except Exception as e:
            self.db.rollback()
            logging.error(e)

    @rpc
    def unpublish_news(self, news_id):
        try:
            news = self.db.query(NewsCommandModel).filter(
                NewsCommandModel.id == news_id
            ).order_by(NewsCommandModel.version.desc())[0]
            data = NewsSchema().dump(news).data
            data['version'] = news.version + 1
            data['status'] = 'UNPUBLISHED'
            data['is_active'] = False
            news_data = NewsCommandModel(data)
            self.db.add(news_data)
            self.db.commit()
            self.dispatcher('news_edited', data)
            return data.get('id')
        except Exception as e:
            self.db.rollback()
            logging.error(e)


class EventsComponet:
    name = 'events_component'
    redis = Redis('cache', encoding='utf-8')

    @event_handler('command_stack', 'news_created')
    def news_created_normalize_db(self, data):
        try:
            del data['version']
            del data['status']
            NewsQueryModel(**data).save()
            self.set_cache(data)
        except Exception as e:
            logging.error(e)

    @event_handler('command_stack', 'news_edited')
    def news_edited_normalize_db(self, data):
        try:
            del data['version']
            del data['status']
            news = NewsQueryModel.objects.get(
                id=data.get('id')
            )
            news.update(**data)
            news.reload()
            self.set_cache(data)
        except Exception as e:
            logging.error(e)

    def set_cache(self, data):
        redis_data = json.dumps(data)
        self.redis.set(data.get('id'), redis_data)
        self.redis.rpush(CACHE_ALL, redis_data)


class QueryNewsService:
    name = 'query_stack'
    redis = Redis('cache', encoding='utf-8')

    @rpc
    def list_news(self, page, limit):
        try:
            if not page:
                page = 1
            offset = (page - 1) * limit

            # gettting list from cache
            news_list = self.redis.lrange(CACHE_ALL, page, limit)
            if news_list:
                return news_list

            news_list = NewsQueryModel.objects.skip(offset).limit(limit)
            return news_list.to_json()
        except Exception as e:
            logging.error(e)
            return json.dumps({'error': str(e)})

    @rpc
    def get_news(self, news_id):
        try:
            # getting from cache
            news = self.redis.get(news_id)
            if news:
                return news
            news = NewsQueryModel.objects.get(id=news_id)
            return news.to_json()
        except mongoengine.DoesNotExist as e:
            logging.error(e)
            return json.dumps({'error': str(e)})
        except Exception as e:
            logging.error(e)
            return json.dumps({'error': str(e)})
