from http import HTTPStatus

from django.urls import reverse

from pytest_django.asserts import assertRedirects, assertFormError

from .conftest import COMMENT_TEXT, NEW_COMMENT_TEXT
from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_anonymous_user_cant_create_comment(
        db, client, form_data, news_pk_for_args
):
    url = reverse('news:detail', args=news_pk_for_args)
    client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(
        db, news, author, author_client, form_data, news_pk_for_args
):
    url = reverse('news:detail', args=news_pk_for_args)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(db, author_client, news_pk_for_args):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=news_pk_for_args)
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(
        db, author_client, form_data, news_pk_for_args, comment_pk_for_args
):
    news_url = reverse('news:detail', args=news_pk_for_args)
    url_to_comments = news_url + '#comments'
    url = reverse('news:delete', args=comment_pk_for_args)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(
        db, not_author_client, form_data, comment_pk_for_args
):
    url = reverse('news:delete', args=comment_pk_for_args)
    response = not_author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
        db,
        author_client,
        new_form_data, comment,
        news_pk_for_args,
        comment_pk_for_args
):
    news_url = reverse('news:detail', args=news_pk_for_args)
    url_to_comments = news_url + '#comments'
    url = reverse('news:edit', args=comment_pk_for_args)
    response = author_client.post(url, data=new_form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text, NEW_COMMENT_TEXT


def test_user_cant_edit_comment_of_another_user(
        db, not_author_client, new_form_data, comment, comment_pk_for_args
):
    url = reverse('news:delete', args=comment_pk_for_args)
    response = not_author_client.post(url, data=new_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT
