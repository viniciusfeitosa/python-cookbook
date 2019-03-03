from flask import request, json, Response, Blueprint
from ..models.news import NewsModel
from ..schema.news import NewsSchema

news_api = Blueprint('news_api', __name__)
news_schema = NewsSchema()


@news_api.route('/', methods=['POST'])
def create_news():
    req_data = request.get_json()
    data, error = news_schema.load(req_data)

    if error:
        return view_response(error, 400)

    news = NewsModel(data)
    news.save()
    response_data = news_schema.dump(news).data
    return view_response(response_data, 201)


@news_api.route('/', methods=['GET'])
def list_news():
    news = NewsModel.list_news()
    response_data = news_schema.dump(news, many=True).data
    return view_response(response_data, 200)


@news_api.route('/<int:news_id>', methods=['GET'])
def get_news(news_id):
    news = NewsModel.get_news(news_id)
    if not news:
        return view_response({'error': 'news not found'}, 404)

    response_data = news_schema.dump(news).data
    return view_response(response_data, 200)


@news_api.route('/', methods=['PUT'])
def update_news():
    request_data = request.get_json()
    data, error = news_schema.load(request_data, partial=True)
    if error:
        return view_response(error, 400)

    news = NewsModel.get_news(data.get('id'))
    news.update(data)
    response_data = news_schema.dump(news).data
    return view_response(response_data, 200)


@news_api.route('/int:news_id', methods=['DELETE'])
def delete_news(news_id):
    news = NewsModel.get_news(news_id)
    news.delete()
    return view_response({'message': 'deleted'}, 204)


def view_response(res, status_code):
    return Response(
        mimetype="application/json",
        response=json.dumps(res),
        status=status_code
    )
