import pytest

from datetime import datetime, timedelta

from django.conf import settings
from django.test.client import Client
from django.utils import timezone

from news.models import Comment, News


COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Обновлённый комментарий'


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )


@pytest.fixture
def some_news():
    today = datetime.today()
    return News.objects.bulk_create(
        News(
            title=f'Новость{index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text=COMMENT_TEXT,
    )


@pytest.fixture
def some_comments(news, author):
    now = timezone.now()
    comment_list = []
    for index in range(10):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
        comment_list.append(comment)
    return comment_list


@pytest.fixture
def news_pk_for_args(news):
    return (news.pk,)


@pytest.fixture
def comment_pk_for_args(comment):
    return (comment.pk,)


@pytest.fixture
def form_data():
    return {'text': COMMENT_TEXT}


@pytest.fixture
def new_form_data():
    return {'text': NEW_COMMENT_TEXT}
